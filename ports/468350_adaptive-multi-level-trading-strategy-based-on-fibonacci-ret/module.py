"""Close crossings of the 100-bar range's retracement lines, 4-hour bars: the close crossing over the 61.8 % line (from the top) goes long, crossing under the 38.2 % line goes short, each with a 50-pip target and 20-pip stop from the signal close; reversing.
Port of FMZ strategy #468350 "Adaptive Multi Level Trading Strategy Based on Fibonacci Retracement" (Simple Fibonacci Retracement Strategy).

FMZ source id: 468350

Source
    https://www.fmz.com/strategy/468350 (PineScript v5, FMZ last modified 2024-09-26 17:21:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-263), 100-bar high / low; direction "Top to Bottom"; buy level 61.8 %, sell level 38.2 %; target 50, stop 20 pips (pip = mintick x 10); 10 % of equity
    crossover(close, high - range x 0.618) -> entry Long + exit(limit = close + 50 pips, stop = close - 20 pips)
    crossunder(close, high - range x 0.382) -> entry Short + exit(limit = close - 50 pips, stop = close + 20 pips)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default inputs the levels are measured from the 100-bar high down. The pips are mintick
      x 10 = 1.0 in price on the 0.1 tick: 50 / 20 price units, ported as fractions of 42000 (0.00119 /
      0.000476 of the fill). The labels are drawing only. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. The 10 % of equity
      size is not ported. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the pip bracket as fractions of the fill.
    2 generic: PASS, retracement-line crossings with a pip bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_468350_range100_fib618_382_cross_pip_bracket_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [100, 50],
    "tp_frac": [0.00119, 0.01],
    "sl_frac": [0.000476, 0.005],
}
DEFAULT_PARAMS = {"lookback": 100, "tp_frac": 0.00119, "sl_frac": 0.000476}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    f618, f382 = hh - (hh - ll) * 0.618, hh - (hh - ll) * 0.382
    le = (c > f618) & (c.shift(1) <= f618.shift(1))
    se = (c < f382) & (c.shift(1) >= f382.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
