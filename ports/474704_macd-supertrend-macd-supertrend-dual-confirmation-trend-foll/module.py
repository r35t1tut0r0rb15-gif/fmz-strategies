"""MACD 12 / 26 / 9 cross-ups above a custom supertrend (2, SMA-of-TR 20), hourly bars, long only: the cross up with the close over the line buys with a 0.5 % stop and a (practically unreachable) 99.99 % target from the signal close.
Port of FMZ strategy #474704 "基于MACD与Supertrend的双重验证趋势跟踪交易策略-MACD-Supertrend-Dual-Confirmation-Trend-Following-Trading-Strategy" (MANTHAN BHRAMASTRA).

FMZ source id: 474704

Source
    https://www.fmz.com/strategy/474704 (PineScript v5, FMZ last modified 2024-12-11 17:16:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-139), supertrend factor 2, ATR = SMA(TR, 20); MACD 12 / 26 / 9; stop close x 0.995, limit close x 1.9999
    st := na(st[1]) ? hl2 : close[1] > st[1] ? max(hl2 - 2 atr, st[1]) : min(hl2 + 2 atr, st[1]);  dir = close > st ? 1 : -1;  crossover(macd, signal) and dir == 1 -> entry Buy, exit(stop = close x 0.995, limit = close x 1.9999)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is the source's own recursion (a loop; math.max / min with na stay na, so it restarts at
      hl2 until the ATR exists). The bracket is sent on the signal bar from its close: sent as fractions
      of the fill open; a level at or through it is marketable and closed one bar late (as #458256). A
      repeat signal inside a trade re-sends it from its own close: the opening levels are kept (as
      #434428, mark trailing_stop_pending). Long only. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, MACD cross-ups over a supertrend line with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474704_macd_cross_custom_supertrend_stop_0p5_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [2, 3],
    "atr_len": [20, 10],
}
DEFAULT_PARAMS = {"factor": 2, "atr_len": 20, "sl_pct": 0.005, "tp_pct": 0.9999}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = tr.rolling(int(p["atr_len"])).mean()
    k = float(p["factor"])
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    upt, dnt = hl2 - k * atr.to_numpy(dtype=float), hl2 + k * atr.to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    st = np.full(len(cv), np.nan)
    for i in range(len(cv)):
        prev = st[i - 1] if i >= 1 else np.nan
        if np.isnan(prev):
            st[i] = hl2[i]
        elif cv[i - 1] > prev:
            st[i] = np.nan if np.isnan(upt[i]) else max(upt[i], prev)
        else:
            st[i] = np.nan if np.isnan(dnt[i]) else min(dnt[i], prev)
    up = pd.Series(cv > st, index=bars_df.index)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & up
    lvl = {"l_sl": c * (1 - float(p["sl_pct"])), "l_tp": c * (1 + float(p["tp_pct"]))}
    return le, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)       # marketable at the fill
    false = pd.Series(False, index=bars_df.index)
    return le, lf & thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
