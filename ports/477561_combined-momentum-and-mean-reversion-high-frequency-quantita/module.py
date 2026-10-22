"""EMA 50 / 400 crossings and Bollinger 20 / 2 re-entries, hourly bars: the EMA cross up or the close crossing back over the lower band goes long, the EMA cross down or the close crossing back under the upper band goes short; reversing.
Port of FMZ strategy #477561 "Combined Momentum and Mean Reversion High Frequency Quantitative Strategy" (Momentum and Mean Reversion Strategy).

FMZ source id: 477561

Source
    https://www.fmz.com/strategy/477561 (PineScript v5, FMZ last modified 2025-01-06 13:58:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-132), EMA 50 / 400 (momentum on); BB 20 / 2 (mean reversion on)
    crossover(ema50, ema400) -> entry Momentum Long;  crossunder -> entry Momentum Short;  crossover(close, lower) -> entry BB Long;  crossunder(close, upper) -> entry BB Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With pyramiding 1 a second id on the held side is ignored, so the four ids act as one long and one
      short entry. On a bar with signals on both sides the later call wins (#437773), in the order
      Momentum Long, Momentum Short, BB Long, BB Short. REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings plus Bollinger re-entries.
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

NAME = "fmz_477561_ema50_400_cross_bb20_reentry_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_ema": [400, 200],
    "bb_length": [20, 50],
}
DEFAULT_PARAMS = {"short_ema": 50, "long_ema": 400, "bb_length": 20, "bb_std": 2.0}


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
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    m_l = (a > b) & (a.shift(1) <= b.shift(1))
    m_s = (a < b) & (a.shift(1) >= b.shift(1))
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_std"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    b_l = (c > dn) & (c.shift(1) <= dn.shift(1))
    b_s = (c < up) & (c.shift(1) >= up.shift(1))
    le = ~b_s & (b_l | (m_l & ~m_s))
    se = b_s | (m_s & ~b_l)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
