"""Close crossings of the displaced Senkou Span B (52-bar midline, 26 bars back), daily bars, long only: crossing over goes long, crossing under closes.
Port of FMZ strategy #449817 "Ichimoku-Leading-Span-B-突破策略-Ichimoku-Leading-Span-B-Breakout-Strategy" (Ichimoku Leading Span B Alım/Satım Stratejisi).

FMZ source id: 449817

Source
    https://www.fmz.com/strategy/449817 (PineScript v5, FMZ last modified 2024-04-29 14:45:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-143), Tenkan 9, Kijun 26, Span B 52, displacement 26
    crossover(close, spanB[26]) -> entry Alım;  crossunder(close, spanB[26]) -> close Alım

Interpretation choices (Pine rules in SURVEY_README.md)
    * The span is compared 26 bars back, the value plotted under the current bar. Tenkan, Kijun and
      Span A are computed and unused. Long only. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the span from 26 bars back.
    2 generic: PASS, displaced Span B crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449817_displaced_span_b_cross_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "span_b": [52, 26],
    "displacement": [26, 13],
}
DEFAULT_PARAMS = {"span_b": 52, "displacement": 26}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["span_b"])
    sb = ((h.rolling(n).max() + lo.rolling(n).min()) / 2).shift(int(p["displacement"]))
    le = (c > sb) & (c.shift(1) <= sb.shift(1))
    lx = (c < sb) & (c.shift(1) >= sb.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
