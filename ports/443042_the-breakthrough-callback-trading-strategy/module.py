"""A cumulative up / down strength ratio against its SMA 50 with an inverted MACD histogram and an EMA 9 / 21 / 50 stack, 1-hour bars: strength above its average with a negative histogram in a falling EMA
stack goes long, the mirror short; reversing.
Port of FMZ strategy #443042 "The Breakthrough Callback Trading Strategy" (Divergence Scalper [30MIN]).

FMZ source id: 443042

Source
    https://www.fmz.com/strategy/443042 (PineScript v5, FMZ last modified 2024-02-28 18:01:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-181), EMA 9 / 21 / 50; strength SMA 50; MACD fast 23 / slow 11 on open, signal SMA 6; commission 0.04
    top = sum of close / close[1] on up bars, bottom = sum of close[1] / close on other bars (from the first bar);  abs = top / (top + bottom);  abs_final = abs - sma(abs, 50)
    long = abs_final > 0 and hist < 0 and ema9 < ema21 < ema50;  short = abs_final < 0 and hist > 0 and ema9 > ema21 > ema50;  long_exit = short;  short_exit = long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strength sums accumulate from the first bar of the data, as written. The MACD has the fast
      length 23 above the slow 11, on the open, as written. The exits equal the opposite entries, so
      they only repeat the reversals. The entries are level tests, refused while held. The commission
      is a cost. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cumulative strength with an MACD / EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commission stored.
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

NAME = "fmz_443042_cumulative_strength_macd_ema_stack_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [23, 12],
    "slow_length": [11, 26],
}
DEFAULT_PARAMS = {"fast_length": 23, "slow_length": 11, "signal_length": 6, "abs_len": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    c1 = c.shift(1)
    up = (c > c1).to_numpy()
    ratio_u = (c / c1).to_numpy()
    ratio_d = (c1 / c).to_numpy()
    m = len(c)
    ab = np.full(m, np.nan)
    top = bot = 0.0
    for i in range(m):
        if up[i]:
            top += ratio_u[i]
        elif i > 0 and not np.isnan(ratio_d[i]):
            bot += ratio_d[i]
        if top + bot / 2 >= 0 and (top + bot) != 0:
            ab[i] = 1 - 1 / (1 + (top / 2) / (bot / 2)) if bot != 0 else np.nan
    a = pd.Series(ab, index=c.index)
    af = a - a.rolling(int(p["abs_len"])).mean()
    e9 = c.ewm(span=9, adjust=False).mean()
    e21 = c.ewm(span=21, adjust=False).mean()
    e50 = c.ewm(span=50, adjust=False).mean()
    macd = o.ewm(span=int(p["fast_length"]), adjust=False).mean() - o.ewm(span=int(p["slow_length"]), adjust=False).mean()
    hist = macd - macd.rolling(int(p["signal_length"])).mean()
    le = (af > 0) & (hist < 0) & (e9 < e21) & (e21 < e50)
    se = (af < 0) & (hist > 0) & (e9 > e21) & (e21 > e50)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
