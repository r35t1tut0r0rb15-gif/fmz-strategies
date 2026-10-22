"""EMA 10 / 20 crossings gated by the EMA 10's run lengths, 3-minute bars: a cross up goes long when more than 3 bars have passed since a falling run of over 5 bars ended; a cross down goes short when more
than 3 bars have passed since a rising run of over 10 bars ended; reversing.
Port of FMZ strategy #439737 "A Momentum Crossover Strategy Based on Exponential Moving Average" (PierceMAStrat).

FMZ source id: 439737

Source
    https://www.fmz.com/strategy/439737 (PineScript v2, FMZ last modified 2024-01-23 14:18:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-237), EMA lengths 2 (unused), 10, 20, 50 (unused)
    ascent = ema10[1] < ema10;  StartUp = not ascent;  AscentBarCounter = barssince(StartUp);  DescentBarCounter = barssince(not StartUp)
    MaxAscent = ABC[1] > ABC and ABC[1] > 10;  MaxDescent = DBC[1] > DBC and DBC[1] > 5;  long = crossover(ema10, ema20) and barssince(MaxDescent) > 3;  short = crossunder and barssince(MaxAscent) > 3

Interpretation choices (Pine rules in SURVEY_README.md)
    * TimeSinceAscensionStart is 0 off a rise and barssince(descent) >= 1 on one, so StartUp is "not
      rising" and StartDown "rising" (an undefined count reads as false, as written). The counters are
      the lengths of the current rising / non-rising runs; MaxAscent / MaxDescent mark the bar a long
      run ends. barssince of a condition that never happened is undefined and blocks the entry.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and run counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439737_pierce_ema10_20_cross_run_gate"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [10, 5],
    "len2": [20, 30],
}
DEFAULT_PARAMS = {"len1": 10, "len2": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _barssince(cond):
    """Pine's barssince: bars since cond was last true (0 on a true bar), undefined before the first."""
    m = len(cond)
    out = np.full(m, np.nan)
    last = -1
    for i in range(m):
        if cond[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return pd.Series(out)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    ascent = (e1.shift(1) < e1).to_numpy()
    descent = (e1.shift(1) > e1).to_numpy()
    bsd = _barssince(descent).to_numpy()
    tsas = np.where(ascent, bsd, 0.0)
    start_up = tsas < 1                                   # an undefined count compares false
    abc = _barssince(start_up)
    dbc = _barssince(~start_up)
    max_asc = ((abc.shift(1) > abc) & (abc.shift(1) > 10)).to_numpy()
    max_des = ((dbc.shift(1) > dbc) & (dbc.shift(1) > 5)).to_numpy()
    bs_ma, bs_md = _barssince(max_asc).to_numpy(), _barssince(max_des).to_numpy()
    xo = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).to_numpy()
    xu = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(xo & (bs_md > 3), index=ix), false, pd.Series(xu & (bs_ma > 3), index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
