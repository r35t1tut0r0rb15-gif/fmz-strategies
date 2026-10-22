"""SMA 10 / 100 crossings with a 10-bar cooldown between signals inside a 00:00-23:59 UTC window, 2-hour bars: the up-cross goes long and the down-cross goes short, each with a 1.5 ATR 14 stop and a 3 ATR target from the signal close; leaving the window closes; reversing.
Port of FMZ strategy #482836 "基于动态ATR和双均线交叉的自适应风险管理策略-Adaptive-Risk-Management-Strategy-Based-on-Dynamic-ATR-and-Moving-Average-Crossover" (Profitable Moving Average Crossover Strategy).

FMZ source id: 482836

Source
    https://www.fmz.com/strategy/482836 (PineScript v5, FMZ last modified 2025-02-20 14:07:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-179), SMA 10 / 100; ATR 14 x 1.5, RR 2; cooldown 10 bars; window 00:00-23:59 UTC; risk 1 % (unused)
    crossover(sma10, sma100) and in window and no cooldown -> entry Buy + exit(stop = close - 1.5 atr, limit = close + 3 atr), lastSignalBar := bar_index
    crossunder(...) likewise -> entry Sell + exit(stop = close + 1.5 atr, limit = close - 3 atr);  not in window -> close Buy / close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The window compares the bar's UTC open time with today's 00:00 and 23:59 UTC, as the source's
      timestamp("UTC", ...) lines do; every 2-hour bar opens inside it at the defaults, so the window
      closes never fire then. The cooldown counts bars since the last signal of either side.
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour:
      mark coarse_bar_stop. riskPercent feeds nothing (no qty is passed). FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, SMA crossings with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (riskPercent unused).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: clock window 00:00-23:59 UTC on the bar's open time (the source's UTC timestamps); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482836_sma10_100_cross_cooldown10_atr1_5_rr2_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_period": [10, 20],
    "long_period": [100, 50],
}
DEFAULT_PARAMS = {"short_period": 10, "long_period": 100, "atr_length": 14, "atr_mult": 1.5, "rr": 2.0,
                  "cooldown": 10, "start_minute": 0, "end_minute": 1439}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _signals(bars_df, p):
    c = bars_df["close"]
    f, s = c.rolling(int(p["short_period"])).mean(), c.rolling(int(p["long_period"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    utc = bars_df.index.tz_convert("UTC")
    mod = np.asarray(utc.hour * 60 + utc.minute)
    valid = (mod >= int(p["start_minute"])) & (mod <= int(p["end_minute"]))
    m = len(up)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = None
    cd = int(p["cooldown"])
    for i in range(m):
        cool = last is not None and (i - last) < cd
        if up[i] and valid[i] and not cool:
            le[i], last = True, i
        if dn[i] and valid[i] and not cool:
            se[i], last = True, i
    off = float(p["atr_mult"]) * _atr(bars_df, int(p["atr_length"]))
    rr = float(p["rr"])
    idx = c.index
    lvl = {"l_sl": c - off, "l_tp": c + off * rr, "s_sl": c + off, "s_tp": c - off * rr}
    return pd.Series(le, index=idx), pd.Series(se, index=idx), pd.Series(~valid, index=idx), lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, out, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = (lf & l_thr) | out
    sx = (sf & s_thr) | out
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
