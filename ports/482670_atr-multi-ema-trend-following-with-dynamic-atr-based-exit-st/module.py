"""EMA 9 / 20 crossings on the EMA 50 side with RSI 14 bands and a 1.1 ATR distance from the EMA 50, hourly bars, at most one signal per day: the cross up goes long with a 2.5 ATR stop and a 3.5 ATR target from the signal close (other multiples for five FX tickers); the short needs a 5-bar regression value of the EMA 50 under 0.2, as written; reversing.
Port of FMZ strategy #482670 "基于多均线趋势和ATR动态止盈止损的加密货币交易策略-Multi-EMA-Trend-Following-with-Dynamic-ATR-Based-Exit-Strategy-for-Cryptocurrency-Trading" (Backtest Last 2880 Baars Filers and Exits).

FMZ source id: 482670

Source
    https://www.fmz.com/strategy/482670 (PineScript v6, FMZ last modified 2025-02-20 14:45:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-187), EMA 9 / 20 / 50; ATR 14; RSI 14 (45-70 buy, 30-55 sell); distance 1.1 ATR; SL / TP by ticker (default 2.5 / 3.5 ATR); one trade per day; 2 % of equity, risk-based qty
    crossover(ema9, ema20) and 45 < rsi < 70 and close > ema50 and close > ema20 and |close - ema50| > 1.1 atr and linreg(ema50, 5, 0) > -0.2 and dailyTradeCount < 1 -> entry Buy + exit(limit = close + tp atr, stop = close - sl atr)
    crossunder mirror (30 < rsi < 55, close under both, linreg(ema50, 5, 0) < 0.2) -> entry Sell + exit;  dayofweek changes -> dailyTradeCount := 0;  each signal -> dailyTradeCount += 1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "slope" filters compare the regression VALUE of the EMA 50 with -0.2 / 0.2, as written: the long
      filter always passes on positive prices and the short one passes only on prices under 0.2. The daily
      counter allows one signal per day of the week change (UTC bar times). The ticker switch is kept: the
      symbol key picks the EURUSD / USDJPY / GBPUSD / AUDUSD / GBPJPY multiples, every other instrument
      the default. The levels are fixed at the signal close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A repeat signal while the side
      is held re-sends the bracket from the new close; stops() keeps the first, so the repeat case is
      marked trailing_stop_pending (as #434428). allowTrade is always true. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The equity-based quantity is sizing. The source carries the Mozilla
      Public License 2.0 notice. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket from the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings with trend-distance and RSI filters, one per day.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: 2 % of equity and the equity-risk quantity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: one signal per UTC day-of-week change; no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482670_ema9_20_cross_ema50_dist_rsi_daily_one_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "min_distance_atr": [1.1, 0.5],
    "rsi_buy_low": [45, 50],
}
DEFAULT_PARAMS = {"min_distance_atr": 1.1, "rsi_buy_low": 45, "atr_length": 14, "rsi_length": 14}
TICKER_MULTS = {"EURUSD": (3.0, 3.8), "USDJPY": (2.5, 3.5), "GBPUSD": (3.0, 4.0),
                "AUDUSD": (3.2, 4.0), "GBPJPY": (3.0, 5.0)}      # (stop, target) ATR multiples


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    key = "".join(ch for ch in str(symbol_key).upper() if ch.isalnum())
    sl_m, tp_m = next((v for k, v in TICKER_MULTS.items() if k in key), (2.5, 3.5))
    bars["sl_mult"] = sl_m
    bars["tp_mult"] = tp_m
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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _linreg(x, n):
    """Pine ta.linreg(x, n, 0): the least-squares line over the last n values, at the last one."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m >= n:
        k = np.arange(n, dtype=float)
        sy = np.convolve(v, np.ones(n))[:m]                        # sum of the window
        sky = np.convolve(v, k)[:m]                                # sum of (age) x value
        sxy = (n - 1) * sy - sky                                   # x = n - 1 - age
        sx, sxx = k.sum(), (k * k).sum()
        b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        a = (sy - b * sx) / n
        out[n - 1:] = (a + b * (n - 1))[n - 1:]
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    c = bars_df["close"]
    e9, e20, e50 = (c.ewm(span=n, adjust=False).mean() for n in (9, 20, 50))
    atr = _atr(bars_df, int(p["atr_length"]))
    r = _rsi(c, int(p["rsi_length"]))
    trending = (c - e50).abs() > atr * float(p["min_distance_atr"])
    lr = _linreg(e50, 5)
    lc = ((e9 > e20) & (e9.shift(1) <= e20.shift(1)) & (r > float(p["rsi_buy_low"])) & (r < 70)
          & (c > e50) & (c > e20) & trending & (lr > -0.2)).to_numpy()
    sc = ((e9 < e20) & (e9.shift(1) >= e20.shift(1)) & (r < 55) & (r > 30)
          & (c < e50) & (c < e20) & trending & (lr < 0.2)).to_numpy()
    dow = bars_df.index.dayofweek
    m = len(lc)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cnt = 0
    for i in range(m):
        if i > 0 and dow[i] != dow[i - 1]:
            cnt = 0
        ok = cnt < 1
        if lc[i] and ok:
            le[i], cnt = True, cnt + 1
        if sc[i] and ok:
            se[i], cnt = True, cnt + 1
    sl = atr * bars_df["sl_mult"]
    tp = atr * bars_df["tp_mult"]
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
    idx = c.index
    return pd.Series(le, index=idx), pd.Series(se, index=idx), lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
