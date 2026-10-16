"""Eltrut (turtle reversed), 4-hour bars, AS WRITTEN long only: the close breaking under the prior 7-bar
low (with Ehlers' trend-flex below 1 and the close above the 3-stdev lower band) goes long; the close
breaking over the prior 7-bar high (trend-flex above -1, close under the upper band) ALSO goes long
(the source's "short" entry is written as a long). Each position has a 3 % stop and a 9 % target.
Port of FMZ strategy #427990 "Eltrut Turtle Reversal Strategy".

FMZ source id: 427990

Source
    https://www.fmz.com/strategy/427990 (PineScript v4, FMZ last modified 2023-09-27 16:30:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 145-249), 7-bar channel, flex 20, BB 35 x 3, SL 3 %, TP 9 %
    trndflx = Ehlers trend-flex of close (super smoother 20, 20-bar sum, 0.04 / 0.96 power average)
    long = crossunder(close, lowest(7)[1]) and trndflx < 1 and close > sma35 - 3 sd
    short = crossover(close, highest(7)[1]) and trndflx > -1 and close < sma35 + 3 sd
    entry("Long", long) when long; entry("Long", long) when short   <- both long
    exit(stop = avg x (1 -+ 3 %), limit = avg x (1 +- 9 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: both signals enter long (decision owed: the intended short side).
    * The IQIFM cycle function is defined but never called. The reflex series is computed but unused.
    * Percent-of-entry levels: sl_stop 0.03, tp_stop 0.09. The date window is unused (if true).
    * Long only. Stop module: portfolio_kwargs {} (driver D4).
    * Stops on 4-hour bars: mark coarse_bar_stop. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, channel lengths, standard deviations and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: slippage and commission settings stored; exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427990_eltrut_trendflex_long"
FAMILY = "channel_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_pct": [3.0, 1.5],
    "take_pct": [9.0, 4.5],
}
DEFAULT_PARAMS = {"chan": 7, "flex_len": 20, "bb_len": 35, "bb_mult": 3.0, "stop_pct": 3.0, "take_pct": 9.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _supersmoother(src, n):
    a = np.exp(-np.sqrt(2) * np.pi / n)
    c2 = 2 * a * np.cos(np.sqrt(2) * np.pi / n)
    c3 = -a * a
    c1 = 1 - c2 - c3
    s = src.to_numpy(dtype=float)
    out = np.full(len(s), np.nan)
    for i in range(len(s)):
        s1 = s[i - 1] if i >= 1 else np.nan
        s2 = s[i - 2] if i >= 2 else np.nan
        o1 = out[i - 1] if i >= 1 else np.nan
        o2 = out[i - 2] if i >= 2 else np.nan
        nz_s1 = s[i] if np.isnan(s1) else s1
        nz_s2 = nz_s1 if np.isnan(s2) else s2
        out[i] = c1 * s[i] + c2 * (nz_s1 if np.isnan(o1) else o1) + c3 * (nz_s2 if np.isnan(o2) else o2)
    return pd.Series(out, index=src.index)


def _trendflex(src, n):
    ss = _supersmoother(src, n)
    total = sum(ss - ss.shift(i) for i in range(1, n + 1)) / n
    t = total.to_numpy()
    out = np.zeros(len(t))
    ms = np.nan
    for i in range(len(t)):
        ms = 0.04 * t[i] ** 2 + 0.96 * (0.0 if np.isnan(ms) else ms)
        out[i] = t[i] / np.sqrt(ms) if (not np.isnan(ms) and ms != 0) else 0.0
    return pd.Series(out, index=src.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["chan"])
    lo7, hi7 = lo.rolling(n).min().shift(1), h.rolling(n).max().shift(1)
    long_c = (c < lo7) & (c.shift(1) >= lo7.shift(1))
    short_c = (c > hi7) & (c.shift(1) <= hi7.shift(1))
    tf = _trendflex(c, int(p["flex_len"]))
    m = int(p["bb_len"])
    basis, dev = c.rolling(m).mean(), p["bb_mult"] * c.rolling(m).std(ddof=0)
    long_s = long_c & (tf < 1) & (c > basis - dev)
    short_s = short_c & (tf > -1) & (c < basis + dev)
    long_e = (long_s | short_s).astype(bool)          # as written: both enter "Long"
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"]) / 100, "tp_stop": float(p["take_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
