"""SMA 10 / 100 crosses with a 10-bar cooldown between signals and a 1.5 ATR stop with a 2 R target, two-hour bars.
Port of FMZ strategy #482836 "基于动态ATR和双均线交叉的自适应风险管理策略-Adaptive-Risk-Management-Strategy-Based-on-Dynamic-ATR-and-Moving-Average-Crossover" (Profitable Moving Average Crossover Strategy).

FMZ source id: 482836

Source
    https://www.fmz.com/strategy/482836 (PineScript v5, FMZ last modified 2025-02-20 14:07:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-179), SMA 10 / 100, window 00:00-23:59 UTC, cooldown 10 bars,
RR 2, ATR 14 x 1.5
    bullish cross and in the window and no signal in the last 10 bars -> entry long with
    exit(stop = close - 1.5 ATR, limit = close + 3 ATR), lastSignalBar = bar_index (short mirrored)
    close both sides when outside the window

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (check 9 / C6): the window is 00:00-23:59 UTC on the bar's opening time; every two-hour bar opens
      inside it, so the window filter and the closes outside it never act (as written, kept as a no-op).
    * The cooldown counts bars since the last signal taken, whatever the position (as written).
    * The bracket is placed with the entry from the signal bar's close: 1.5 ATR / close and RR x that, shifted one bar
      inside stops(), re-based on the fill (house rule); fixed, not re-issued.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, two SMAs and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity and the 1 % risk input quoted; the bracket via stops(), quoted in
      original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (a 00:00-23:59 UTC window that every bar meets).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482836_sma10_100_cross_cooldown_atr_rr"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 100, "cooldown": 10, "atr_len": 14, "atr_mult": 1.5, "rr": 2.0}


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
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    bull = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    bear = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    cd = int(p["cooldown"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = None
    for i in range(m):
        cooling = last is not None and i - last < cd
        if bull[i] and not cooling:
            le[i], last = True, i
        if bear[i] and not cooling:
            se[i], last = True, i
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
