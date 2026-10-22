"""Undisplaced cloud colour with an extra midline, daily bars: leading line 1 (mean of the 9, 26 and 17-bar midlines) above leading line 2 (mean of the 39 and 52-bar midlines) goes long, below goes short;
reversing.
Port of FMZ strategy #445451 "Ichimoku Cloud Local Trend Identification Strategy" (Advanced_Ichimoku_Cloud_Strategy).

FMZ source id: 445451

Source
    https://www.fmz.com/strategy/445451 (PineScript v5, FMZ last modified 2024-03-19 15:10:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-198), conversion 9, base 26, span B 52, PPL1 17, PPL2 39; displacement 26 (plot only); stop multipliers 1.618 / 0.618 (plot only); margins 100 / 100
    leadLine1 = avg(mid(9), mid(26), mid(17));  leadLine2 = avg(mid(39), mid(52));  leadLine1 > leadLine2 -> entry Buy;  leadLine1 < leadLine2 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The leading lines are compared on the bar they are computed, not displaced (the offset is only
      in the plots); ta.lowest / ta.highest without a source use low / high. The stop lines only plot.
      Both conditions are levels, so a repeated entry while already on that side is ignored.
      strategy.entry reverses: REVERSAL INTENDED. The margin settings are sizing. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; no displacement in the rules.
    2 generic: PASS, leading-line order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
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

NAME = "fmz_445451_lead_lines_17_39_order_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ppl1": [17, 9],
    "ppl2": [39, 26],
}
DEFAULT_PARAMS = {"ppl1": 17, "ppl2": 39, "conv": 9, "base": 26, "span_b": 52}


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
    h, lo = bars_df["high"], bars_df["low"]

    def mid(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    l1 = (mid(p["conv"]) + mid(p["base"]) + mid(p["ppl1"])) / 3
    l2 = (mid(p["ppl2"]) + mid(p["span_b"])) / 2
    le = l1 > l2
    se = l1 < l2
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
