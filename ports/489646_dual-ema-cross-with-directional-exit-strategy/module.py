"""EMA 5 / 21 crosses, always in, broker days: EMA 5 crossing above EMA 21 goes long (closing a short), crossing below
goes short (closing a long).
Port of FMZ strategy #489646 "双指数移动平均交叉转向退出策略-Dual-EMA-Cross-with-Directional-Exit-Strategy" (EMA Cross Strategy with EMA Turning Exit).

FMZ source id: 489646

Source
    https://www.fmz.com/strategy/489646 (PineScript v6, FMZ last modified 2025-04-07 12:00:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 180-206), EMA 5 / 21
    crossover(ema5, ema21) and position <= 0 -> close "Short", entry long
    crossunder(ema5, ema21) and position >= 0 -> close "Long", entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The title's "EMA turning exit" is not in the code: the only exits are the reversals. The position gates equal
      the engine ignoring a same-side entry. REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_489646_ema_5_21_cross_always_in"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 21}


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
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((ef > es) & (ef.shift(1) <= es.shift(1))).astype(bool)
    dn = ((ef < es) & (ef.shift(1) >= es.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
