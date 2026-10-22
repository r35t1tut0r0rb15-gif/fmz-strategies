"""RSI hidden bullish divergence in an EMA uptrend, 1-minute bars, long only: with the EMA 50 above the EMA 250 and three closes above the EMA 50, a stochastic (4 / 4 / 3) up-cross within ten bars
of a hidden bullish divergence goes long; a stop at the prior 38-bar low and a target 1.6 times that distance.
Port of FMZ strategy #440847 "基于EMA和隐藏背离的趋势追踪策略EMA-RSI-Hidden-Divergence-Trend-Following-Strategy" (Hidden Div Strat).

FMZ source id: 440847

Source
    https://www.fmz.com/strategy/440847 (PineScript v4, FMZ last modified 2024-02-02 16:54:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-234), EMA 50 / 250; stochastic 4 / 4 / 3; RSI 14 pivots 19 left / 1 right, range 4-20; profit factor 1.6; lowest-low look-back 38; dates from 2020
    plFound = pivotlow(rsi, 19, 1);  hidden bull = low[1] above the previous pivot's low[1] and rsi[1] below the previous pivot's rsi[1] (that pivot 4-20 bars back) and plFound;  buy if one came in the last 10 bars
    longcondition = ema50 > ema250 and close[1..3] > ema50[1..3] (and ema250 non-zero) and k >= d and k[1] <= d[1] and buyhiddenbull;  stop = lowest(low, 38)[1] at the fill bar, target = avg + (avg - stop) x 1.6

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivots are confirmed one bar after their centre (past bars only). The "and ema2[1]" terms are
      truthiness tests that always hold. The stop is the lowest low of the 38 bars up to the signal bar
      (lowest(low, 38)[1] seen from the fill bar): sl_stop = (close - that low) / close of the signal bar,
      tp_stop = 1.6 x sl_stop, shifted one bar inside stops() and re-based on the fill (as #434998; the
      script measures from the fill price and sends them from the fill bar's close on). Entries only
      from flat (pyramiding 0). The date window is dropped. Long only. Stop module: portfolio_kwargs {}
      (driver D4). The 10 % of equity size and capital are sizing. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, EMA trend, stochastic cross and RSI hidden divergence.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity and capital settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440847_rsi_hidden_divergence_ema_trend_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "profitfactor": [1.6, 2.5],
    "lo_len": [38, 20],
}
DEFAULT_PARAMS = {"profitfactor": 1.6, "lo_len": 38, "len1": 50, "len2": 250, "period_k": 4, "period_d": 4,
                  "smooth_k": 3, "rsi_len": 14, "lb_r": 1, "lb_l": 19, "range_upper": 20, "range_lower": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _pivot_low(x, left, right):
    c = x.shift(right)
    ok = c.notna()
    for k in range(1, left + 1):
        ok &= c < x.shift(right + k)
    for k in range(right):
        ok &= c < x.shift(k)
    return ok


def _signal(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    pk = int(p["period_k"])
    ll, hh = lo.rolling(pk).min(), h.rolling(pk).max()
    k = (100.0 * (c - ll) / (hh - ll).where(hh > ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["period_d"])).mean()
    osc = _rsi(c, int(p["rsi_len"]))
    r = int(p["lb_r"])
    pl = _pivot_low(osc, int(p["lb_l"]), r).to_numpy()
    o1, l1 = osc.shift(r).to_numpy(), lo.shift(r).to_numpy()
    m = len(c)
    hb = np.zeros(m, dtype=bool)
    hist_o, hist_l = [], []
    last_pl = -1                                          # bar of the most recent plFound before this bar
    for i in range(m):
        prev_pl = last_pl
        if pl[i]:
            hist_o.append(o1[i])
            hist_l.append(l1[i])
        bars = (i - 1 - prev_pl) if prev_pl >= 0 else -1  # barssince(plFound[1])
        in_range = prev_pl >= 0 and int(p["range_lower"]) <= bars <= int(p["range_upper"])
        if pl[i] and len(hist_o) >= 2:
            osc_ll = o1[i] < hist_o[-2] and in_range
            price_hl = l1[i] > hist_l[-2]
            hb[i] = bool(osc_ll and price_hl)
        if pl[i]:
            last_pl = i
    hbs = pd.Series(hb, index=c.index)
    recent = pd.Series(False, index=c.index)
    for j in range(1, 11):
        recent |= hbs.shift(j, fill_value=False)
    up3 = pd.Series(True, index=c.index)
    for j in range(1, 4):
        up3 &= c.shift(j) > e1.shift(j)
    cross = (k >= d) & (k.shift(1) <= d.shift(1))
    return ((e1 > e2) & up3 & cross & recent).to_numpy()


def _levels(bars_df, p):
    c = bars_df["close"]
    stop = bars_df["low"].rolling(int(p["lo_len"])).min()     # = lowest(low, 38)[1] seen from the fill bar
    sl = ((c - stop) / c).where(c > stop)
    return sl, float(p["profitfactor"]) * sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sig = _signal(bars_df, p)
    sl_s, tp_s = _levels(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if not np.isnan(s_) and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _levels(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
