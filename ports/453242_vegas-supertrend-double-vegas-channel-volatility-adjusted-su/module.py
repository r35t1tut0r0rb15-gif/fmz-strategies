"""Two Vegas-channel-adjusted SuperTrends (ATR 10 / 100-bar channel, ATR 5 / 200-bar channel), 3-hour bars: both trends up is long, both down is short; a trade is closed 5 days after the last bar its alignment held; reversing.
Port of FMZ strategy #453242 "双重Vegas通道波动性调整SuperTrend量化交易策略-Double-Vegas-Channel-Volatility-Adjusted-SuperTrend-Quantitative-Trading-Strategy" (Double Vegas SuperTrend Enhanced - Strategy [presentTrading]).

FMZ source id: 453242

Source
    https://www.fmz.com/strategy/453242 (PineScript v5, FMZ last modified 2024-06-03 11:16:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 68-268), SuperTrend 1: ATR 10, Vegas SMA / SD 100, multiplier 5 + 5 x width / SMA; SuperTrend 2: ATR 5, 200, 7 + 7 x width / SMA; hold 5 days; TPSL None; 10 % of equity, commission 0.1 %, slippage 1
    trend = close > prev lower-line ? 1 : close < prev upper-line ? -1 : trend[1];  lines ratchet with the trend (upper = hlc3 - m x atr, lower = hlc3 + m x atr)
    both trends 1 -> close Short if short, entry Long, longEntryTime = time;  both -1 -> close Long if long, entry Short, shortEntryTime = time
    long and time >= longEntryTime + 5 days -> close Long (the same for shorts);  the entry block runs again at the end

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend lines are built as written (the 'upper' line sits under the price and ratchets
      up in an up trend, the 'lower' over it and ratchets down in a down trend). The entry time is
      reset on every aligned bar, so the 5-day hold counts from the last bar both trends agreed; with
      useHoldDays true (the default) the trend-change exits are disabled, and an opposite alignment
      reverses. TPSL 'None' places no bracket. The hold is measured on the bar open times. REVERSAL
      INTENDED. The 10 % of equity, commission and slippage are stored. FREQ = "3h" from the backtest
      header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, aligned volatility-adjusted SuperTrends with a time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing, commission and slippage stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453242_double_vegas_supertrend_hold_days_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult1": [5.0, 3.0],
    "mult2": [7.0, 5.0],
    "hold_days": [5, 10],
}
DEFAULT_PARAMS = {"mult1": 5.0, "mult2": 7.0, "hold_days": 5, "atr1": 10, "win1": 100, "adj1": 5.0,
                  "atr2": 5, "win2": 200, "adj2": 7.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _vegas_trend(bars_df, atr_n, win, base, adj):
    c = bars_df["close"]
    hlc3 = (bars_df["high"] + bars_df["low"] + c) / 3
    sma, sd = c.rolling(int(win)).mean(), c.rolling(int(win)).std(ddof=0)
    mult = base + adj * (2 * sd / sma)
    atr = _atr(bars_df, atr_n)
    up_raw = (hlc3 - mult * atr).to_numpy()
    lo_raw = (hlc3 + mult * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upv, lov, tr = np.full(m, np.nan), np.full(m, np.nan), np.ones(m, dtype=int)
    t = 1
    for i in range(m):
        pu = upv[i - 1] if i > 0 and not np.isnan(upv[i - 1]) else up_raw[i]
        pl = lov[i - 1] if i > 0 and not np.isnan(lov[i - 1]) else lo_raw[i]
        if cv[i] > pl:
            t = 1
        elif cv[i] < pu:
            t = -1
        u, l_ = up_raw[i], lo_raw[i]
        if t == 1:
            u = np.nan if (np.isnan(u) or np.isnan(pu)) else max(u, pu)
        if t == -1:
            l_ = np.nan if (np.isnan(l_) or np.isnan(pl)) else min(l_, pl)
        upv[i], lov[i], tr[i] = u, l_, t
    return tr, upv, lov


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t1, u1, l1 = _vegas_trend(bars_df, p["atr1"], p["win1"], float(p["mult1"]), float(p["adj1"]))
    t2, u2, l2 = _vegas_trend(bars_df, p["atr2"], p["win2"], float(p["mult2"]), float(p["adj2"]))
    u1p, u2p = np.concatenate(([np.nan], u1[:-1])), np.concatenate(([np.nan], u2[:-1]))
    l1p, l2p = np.concatenate(([np.nan], l1[:-1])), np.concatenate(([np.nan], l2[:-1]))
    go_l = (t1 == 1) & (t2 == 1) & ~np.isnan(u1p) & ~np.isnan(u2p)
    go_s = (t1 == -1) & (t2 == -1) & ~np.isnan(l1p) & ~np.isnan(l2p)
    tm = bars_df.index
    hold = pd.Timedelta(days=int(p["hold_days"]))
    m = len(tm)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, lt, st = 0, None, None
    for i in range(m):
        cur = pos
        if go_l[i]:
            lt = tm[i]
            if cur != 1:
                cur = 1
        if go_s[i]:
            st = tm[i]
            if cur != -1:
                cur = -1
        if lt is not None and tm[i] >= lt + hold and pos == 1 and cur == 1:
            cur, lt = 0, None
        if st is not None and tm[i] >= st + hold and pos == -1 and cur == -1:
            cur, st = 0, None
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
