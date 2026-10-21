"""Stochastic crossings with a pivot-moved stop, broker days: the slow stochastic K (13 / 4) crossing over D (3) below 80 goes long, crossing under above 20 goes short, reversing; the author's stop (at the last
pivot low / high, moved to each new pivot while in the trade) and 400-tick target are described, not emitted.
Port of FMZ strategy #437543 "Moving Stop Loss Tracking Strategy" (Moving Stop-Loss mechanism).

FMZ source id: 437543

Source
    https://www.fmz.com/strategy/437543 (PineScript v4, FMZ last modified 2024-01-03 16:15:29).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-214), stochastic 13 / smooth 4 / D 3; take profit 400 ticks; stop-loss modification on
    GoLong = crossover(k, d) and k < 80;  GoShort = crossunder(k, d) and k > 20;  stoploss_long = min(low, last pivot low) at entry, moved to each new pivot low (pivotlow(low, 1, 1)) while long
    entry Long / Short;  exit(stop = stoploss_long / short, profit = 400) re-sent every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is moved after entry (to every newly confirmed 1 / 1 pivot), which stops() cannot express;
      it is kept pending with its 400-tick target (rule 2, mark trailing_stop_pending; ticks -> ATR when
      expressed: 400 ticks of 0.1 on BTC against a daily ATR near 1000, about 0.04 ATR). Positions end at
      the opposite entry until then. The alert texts place no orders. REVERSAL INTENDED. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, stochastic levels; the pivot stop and tick target are pending.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick target input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437543_stoch_cross_pivot_stop"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_k": [13, 9],
    "smooth_k": [4, 3],
}
DEFAULT_PARAMS = {"period_k": 13, "smooth_k": 4, "period_d": 3}


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
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["period_d"])).mean()
    up = (k > d) & (k.shift(1) <= d.shift(1)) & (k < 80)
    dn = (k < d) & (k.shift(1) >= d.shift(1)) & (k > 20)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
