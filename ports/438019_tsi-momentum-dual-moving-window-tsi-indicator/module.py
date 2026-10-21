"""True Strength Index signal crossings, broker days: the TSI (25, 13) crossing over its EMA 13 goes long, crossing under goes short; reversing.
Port of FMZ strategy #438019 "动量双滑窗TSI指标Momentum-Dual-Moving-Window-TSI-Indicator" (TSI BTCUSD 2H).

FMZ source id: 438019

Source
    https://www.fmz.com/strategy/438019 (PineScript v2, FMZ last modified 2024-01-08 11:20:35).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 161-205), timeframe "120" (2 hours, on a 1-day chart); TSI 25 / 13, signal 13; capital 1000, 100 % of equity, commission 0.2 %, pyramiding 10; date window true
    price = security(tickerid, "120", close);  tsi = 100 x ema(ema(change(price), 25), 13) / ema(ema(abs(change(price)), 25), 13);  tsi2 = ema(tsi, 13)
    crossover(tsi, tsi2) -> entry BUY;  crossunder(tsi, tsi2) -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2-hour close requested from a daily chart is the day's LAST 2-hour bar (a lower time frame
      returns its last bar inside the chart bar); counted from the broker day's start (17:00
      America/New_York) its close is the broker day's close, so the TSI runs on the daily closes.
      Crossings alternate, so pyramiding 10 never adds. strategy.entry reverses: REVERSAL INTENDED. The
      capital, size and commission are sizing / costs. Daily bars are broker days, stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TSI signal crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital, percent-of-equity size, commission and pyramiding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438019_tsi_signal_cross_daily"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long": [25, 40],
    "short": [13, 7],
}
DEFAULT_PARAMS = {"long": 25, "short": 13, "signal": 13}


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


def _ds(x, a, b):
    return x.ewm(span=a, adjust=False).mean().ewm(span=b, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    pc = c.diff()
    a, b = int(p["long"]), int(p["short"])
    with np.errstate(divide="ignore", invalid="ignore"):
        tsi = 100.0 * _ds(pc, a, b) / _ds(pc.abs(), a, b)
    sig = tsi.ewm(span=int(p["signal"]), adjust=False).mean()
    up = (tsi > sig) & (tsi.shift(1) <= sig.shift(1))
    dn = (tsi < sig) & (tsi.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
