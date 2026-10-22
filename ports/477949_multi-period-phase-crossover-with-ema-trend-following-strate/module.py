"""SMA 20 (plus 0.5) against EMA 20 (minus 0.5) crossings, broker days, long only: the SMA line crossing over the EMA line buys, crossing under closes.
Port of FMZ strategy #477949 "Multi Period Phase Crossover with EMA Trend Following Strategy" (Phase Cross Strategy with Zone).

FMZ source id: 477949

Source
    https://www.fmz.com/strategy/477949 (PineScript v5, FMZ last modified 2025-01-10 15:17:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-148), length 20; offset 0.5 (price); EMA 13 / 26 / 50 / 100 / 200 plotted only
    lead = sma(close, 20) + 0.5;  lag = ema(close, 20) - 0.5;  crossover(lead, lag) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 0.5 offset is a price amount, ported as a fraction of 42000 of the close (1.19e-05): the lines
      cross when SMA - EMA crosses minus twice the offset. The EMA crossings below the strategy only plot. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA / EMA crossings with a small offset.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477949_sma20_ema20_offset_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "offset_frac": [1.19e-05, 0.0],
}
DEFAULT_PARAMS = {"length": 20, "offset_frac": 1.19e-05}


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
    off = float(p["offset_frac"]) * c
    lead = c.rolling(n).mean() + off
    lag = c.ewm(span=n, adjust=False).mean() - off
    le = (lead > lag) & (lead.shift(1) <= lag.shift(1))
    lx = (lead < lag) & (lead.shift(1) >= lag.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
