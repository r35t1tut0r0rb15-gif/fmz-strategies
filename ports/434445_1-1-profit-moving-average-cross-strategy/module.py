"""SMA 10 / 30 crosses on 3-day bars, as written: a cross up goes long, a cross down goes short (reversing). The long's
"1 % profit" exit is written as a profit of 0.01 ticks, i.e. a target a fraction of a tick above the fill, so a long
closes at the first trade above its entry; shorts have no exit but the next cross up.
Port of FMZ strategy #434445 "均线黄金交叉1止盈策略1-Profit-Moving-Average-Cross-Strategy" (1% Profit Strategy).

FMZ source id: 434445

Source
    https://www.fmz.com/strategy/434445 (PineScript v4, FMZ last modified 2023-12-06 13:53:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-179), SMA 10 / 30; profit input 1 -> profit = 1 / 100 (ticks)
    crossover(sma10, sma30) -> entry long;  crossunder -> entry short
    position_size > 0 -> exit long (profit = profitPercentage / 100)   (profit is in ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit's profit is a distance in ticks: 0.01 tick. As written the target sits a hundredth
      of a tick above the fill; the port uses tp_stop 1e-6 of the fill (as written; the intended 1 %
      target is owed). Pine arms the exit from the bar after the fill; the engine's minute stops can
      act within the fill bar (approximation stated).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Multi-day bars are blocks of 3 broker days (17:00 America/New_York) counted from 1970-01-01,
      each stamped with its first minute; stops on them: mark coarse_bar_stop. FREQ = "3D" from the
      backtest header (period 3d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long target fixed at entry.
    2 generic: PASS, average crosses and a fill-relative target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker days (17:00 America/New_York, DST by the zone), 3-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434445_sma_cross_tick_target"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of 3 broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 5],
    "slow": [30, 60],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "tp_frac": 1e-6, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    se = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _ = _signals(bars_df, p)
    ix = bars_df.index
    tp = pd.Series(np.where(le, float(p["tp_frac"]), np.nan), index=ix)
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
