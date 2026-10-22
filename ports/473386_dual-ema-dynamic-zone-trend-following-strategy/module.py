"""CDC Action Zone, daily bars, long only: EMA 12 over EMA 26 with the close over the EMA 12 is the green zone, the mirror the red zone; the first green bar buys, the first red bar sells.
Port of FMZ strategy #473386 "Dual EMA Dynamic Zone Trend Following Strategy" (NUTJP CDC ActionZone 2024).

FMZ source id: 473386

Source
    https://www.fmz.com/strategy/473386 (PineScript v5, FMZ last modified 2024-11-29 16:12:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-150), EMA 12 / 26 of close, smoothing 1; fixed-timeframe mode off; qty 1; commission 0.1 %, slippage 3
    Green = fast > slow and price > fast;  Red = fast < slow and price < fast;  Green and not Green[1] -> entry Long (qty 1);  Red and not Red[1] -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Smoothing 1 leaves the close as the price. The fixed-timeframe mode (a security call with
      lookahead on) is off by default and not ported. The date window is always true. Long only. The
      costs and the fixed qty are not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA action zones.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed qty, commission and slippage stored, not ported.
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

NAME = "fmz_473386_cdc_action_zone_ema12_26_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26}


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
    f, s = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    green = (f > s) & (c > f)
    red = (f < s) & (c < f)
    le = green & ~green.shift(1, fill_value=False)
    lx = red & ~red.shift(1, fill_value=False)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
