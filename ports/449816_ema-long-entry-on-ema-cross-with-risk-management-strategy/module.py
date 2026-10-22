"""Close crossings over the EMA 20 buy, daily bars, long only. The 1 % / 2 % bracket from the average price is armed only by a close crossing back under the EMA inside a trade and is not ported, so the port
has no exit (one long held from the first signal).
Port of FMZ strategy #449816 "基于EMA交叉的风险管理型多头策略-Long-Entry-on-EMA-Cross-with-Risk-Management-Strategy" (Long Entry on EMA Cross with Risk Management).

FMZ source id: 449816

Source
    https://www.fmz.com/strategy/449816 (PineScript v4, FMZ last modified 2024-04-29 14:39:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-143), EMA 20; stop 1 %, target 2 % of the average price; trailing 0.5 % of the close (passed as a tick offset)
    crossover(close, ema20) -> entry Long;  exit(stop = avg x 0.99, limit = avg x 1.02, trail_offset = trailing level, when = crossunder(close, ema20))

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is created only on a bar where the close crosses under the EMA, with levels from
      the average price: the bracket appears only inside the trade and then stays. A stop that starts
      after entry cannot be expressed by stops(): it is not ported (as #437800) and the module gets the
      mark trailing_stop_pending (the intended bracket is owed). The trail_offset is a price passed as
      ticks with no trail price or points, so it never activates. Without the bracket the port has no
      exit. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, close / EMA cross-ups.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the percent bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_449816_close_ema20_cross_long_entries"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
}
DEFAULT_PARAMS = {"ema_len": 20}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = (c > e) & (c.shift(1) <= e.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
