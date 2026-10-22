"""SMA 34 +- 1 standard deviation states, daily bars: a close over the upper line is long, under the lower line is short; reversing.
Port of FMZ strategy #453232 "Bollinger-Bands-Accurate-Entry-And-Risk-Control-Strategy-Bollinger-Bands准确入场和风险控制策略" (Bollinger Bands Strategy (one-deviation band states)).

FMZ source id: 453232

Source
    https://www.fmz.com/strategy/453232 (PineScript v5, FMZ last modified 2024-06-03 10:53:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-132), SMA 34; 1 SD bands (the 2 SD bands unused)
    close > basis + sd -> entry Long;  close < basis - sd -> entry Short;  the short condition closes Long, the long condition closes Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are states (ignored while held) and are called before the closes, so each close
      finds its trade already reversed by the entry on the same bar: plain reversals. The multiplier
      only sets the 2-deviation lines, which no order uses. REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, one-deviation band states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453232_sma34_one_sd_band_state_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20, 50],
}
DEFAULT_PARAMS = {"length": 34}


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
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    false = pd.Series(False, index=bars_df.index)
    return c > basis + sd, false, c < basis - sd, false.copy()


def portfolio_kwargs(**params):
    return {}
