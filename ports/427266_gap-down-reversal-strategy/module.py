"""Gap-down reversal, long only: a bar that opens below the previous close and closes above its open
goes long; a trailing stop 5 % under the highest close since entry protects the long.
Port of FMZ strategy #427266 "Gap Down Reversal Strategy".

FMZ source id: 427266

Source
    https://www.fmz.com/strategy/427266 (PineScript v2, FMZ last modified 2023-09-19 16:19:51).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 189-244), trail 5 %, start date 2009-01-01
    gap_d_r = open < close[1] and close > open -> entry long (pyramiding 1)
    longStopPrice = position > 0 ? max(close x (1 - 5 %), longStopPrice[1]) : 0
    position > 0 -> exit(stop = longStopPrice)

Interpretation choices (Pine rules in SURVEY_README.md; skill 30-strategy-authoring section 7)
    * The stop ratchets on bar closes and is placed as a stop order for the next bar: on the
      source's 1-minute bars this is exactly the house trailing stop
      {"type": "percent", "pct": 0.05, "anchor": "close"} (level = the best minute close up to the
      previous minute x (1 - pct), never retreats). Ported natively: mark trailing_stop
      (replaces trailing_stop_pending, FMZ-C rule 1).
    * pyramiding 1: entries only from flat: Opposite entries cannot occur (long only).
    * The start date (2009) is the author's backtest window: dropped.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the trailing stop is the house trail.
    2 generic: PASS, a candle rule and a percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash qty 10000 stored in original_sizing.txt; the trail is ported via stops().
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (a "gap" here is open below the previous close on 1-minute bars, no session rule).
Long only. Opposite entries cannot occur.

Marks: trailing_stop
"""
import pandas as pd

NAME = "fmz_427266_gap_down_reversal_trail"
FAMILY = "candle_pattern"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [5.0, 2.0, 10.0],
}
DEFAULT_PARAMS = {"trail_pct": 5.0}


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
    o, c = bars_df["open"], bars_df["close"]
    entry = ((o < c.shift(1)) & (c > o)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return entry, false.copy(), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": p["trail_pct"] / 100, "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
