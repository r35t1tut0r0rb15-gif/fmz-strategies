"""EMA rainbow pullback entries with an 8 % close trail, long only, broker days: with the EMAs 10 > 20 > 50 and 100 > 150 > 200, the close crossing over the EMA 10 or the EMA 10 crossing over the EMA 20 goes
long; the trade exits on a trail 8 % under its best close.
Port of FMZ strategy #439620 "Multi EMA Bullish Trend Strategy" (SirSeff's EMA Rainbow).

FMZ source id: 439620

Source
    https://www.fmz.com/strategy/439620 (PineScript v5, FMZ last modified 2024-01-22 12:04:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-195), test period 2000-01-01 to 2100-12-30 (covers the data); long trailing stop 8 %
    longCondition = ema10 > ema20 > ema50 and ema100 > ema150 > ema200;  entry BUY1 on crossover(close, ema10);  entry BUY2 on crossover(ema10, ema20)
    longStopPrice = position > 0 ? max(close x 0.92, longStopPrice[1]) : 0;  exit(TSP, stop = longStopPrice) while long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop ratchets 8 % under the best bar close of the trade: read as the house percent trail, 8 %
      behind the best close (anchor close; the original takes daily closes from the fill bar on, the
      house trail minute closes: stated approximation; mark trailing_stop). One position is held
      (pyramiding 1). The test period covers the data (#436533). Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code. Daily
      bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: PASS, EMA stack and crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439620_ema_rainbow_pullback_close_trail_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail": [0.08, 0.04],
}
DEFAULT_PARAMS = {"trail": 0.08}


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
    c = bars_df["close"]
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (10, 20, 50, 100, 150, 200)}
    cond = (e[10] > e[20]) & (e[20] > e[50]) & (e[100] > e[150]) & (e[150] > e[200])
    x1 = (c > e[10]) & (c.shift(1) <= e[10].shift(1))
    x2 = (e[10] > e[20]) & (e[10].shift(1) <= e[20].shift(1))
    false = pd.Series(False, index=c.index)
    return cond & (x1 | x2), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail"]), "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
