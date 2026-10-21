"""SuperTrend pullbacks with EMA 200, RSI, MACD and CCI filters, 5-minute bars: from flat, in a SuperTrend (10, 3) uptrend, the previous bar's low crossing under the line with a higher high, the close above the
EMA 200, the RSI 14 at or above 50, the MACD line above 0 and the CCI 20 above 200 goes long; the mirror goes short; each trade has a 1 % stop and a 2 % target from the fill.
Port of FMZ strategy #438004 "Supertrend Advance Strategy" (Supertrend advance).

FMZ source id: 438004

Source
    https://www.fmz.com/strategy/438004 (PineScript v5, FMZ last modified 2024-01-08 10:03:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 227-399), type Pullback; Sl/Tp Percentage (stop 1 %, take 2 %, trail off); SuperTrend ATR 10, factor 3; EMA 200; RSI 14 at 50 / 50; MACD 12 / 26 / 9; CCI 20 at 200 / -200; direction Both; quantity 1
    fin_pullbuy = crossunder(low[1], long line) and long line and high > high[1];  fin_pullsell = crossover(high[1], short line) and short line and low < low[1]
    buy_cond = fin_pullbuy and rsi >= 50 and close > ema 200 and macd > 0 and cci > 200;  sell_cond mirror (rsi <= 50, close < ema 200, macd < 0, cci < -200)
    position_size == 0 -> entry long / short;  in position: exit(stop = avg x (1 -/+ 1 %), limit = avg x (1 +/- 2 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long (short) line is the SuperTrend value in an uptrend (downtrend), na otherwise, and is
      true as a condition when it is a value. The default exit type is Percentage: the bracket is sent
      from the first bar close inside the trade (one bar after the fill); the port fixes it at entry
      (sl_stop = 0.01, tp_stop = 0.02 of the fill). The Supertrend, Swinghl and ATR exit types are not
      selected and not ported (their inputs stored). "Flat" follows the house bracket (the loop marks the
      trade closed when a bar's low or high reaches a level from the fill price). Entries only from flat:
      Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). The 1 % of equity and
      the quantity 1 are sizing. time_cond is true. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, SuperTrend, EMA, RSI, MACD and CCI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, the quantity input and the unselected exit types stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438004_supertrend_pullback_filters_bracket"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "cci_level": [200, 100],
}
DEFAULT_PARAMS = {"factor": 3.0, "cci_level": 200, "atr_period": 10, "ema_len": 200, "rsi_len": 14,
                  "rsi_level": 50.0, "fast": 12, "slow": 26, "signal": 9, "cci_len": 20, "stop": 0.01,
                  "take": 0.02}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _supertrend(h, lo, c, factor, n):
    """Pine's ta.supertrend(factor, atrPeriod): (line, direction), direction -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return st, d


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (src - ma) / (0.015 * dev)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    ix = bars_df.index
    st, d = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    lng = pd.Series(np.where(d < 0, st, np.nan), index=ix)
    sht = pd.Series(np.where(d < 0, np.nan, st), index=ix)
    l1, h1 = lo.shift(1), h.shift(1)
    pull_b = (l1 < lng) & (l1.shift(1) >= lng.shift(1)) & lng.notna() & (lng != 0) & (h > h1)
    pull_s = (h1 > sht) & (h1.shift(1) <= sht.shift(1)) & sht.notna() & (sht != 0) & (lo < l1)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    cci = _cci((h + lo + c) / 3.0, int(p["cci_len"]))
    lvl = float(p["cci_level"])
    buy = (pull_b & (r >= float(p["rsi_level"])) & (c > ema) & (macd > 0) & (cci > lvl)).to_numpy()
    sell = (pull_s & (r <= float(p["rsi_level"])) & (c < ema) & (macd < 0) & (cci < -lvl)).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["stop"]), float(p["take"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + sl) or lv[i] <= e * (1 - tp)):
                pos = 0
        if pos == 0 and i + 1 < m:
            if buy[i]:
                le[i], pos, entry_i = True, 1, i + 1
            elif sell[i]:
                se[i], pos, entry_i = True, -1, i + 1
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"]), "tp_stop": float(p["take"])}


def portfolio_kwargs(**params):
    return {}
