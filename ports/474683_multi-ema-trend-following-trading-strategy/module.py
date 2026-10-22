"""EMA 30 re-crossings in an EMA 10 / 30 / 50 trend, daily bars: in an up-trend (10 > 30 > 50) a close crossing over the EMA 30 goes long, closed when the EMA 30 crosses under the EMA 50; the down-trend mirror goes short, closed when the EMA 30 crosses over the EMA 50; reversing.
Port of FMZ strategy #474683 "Multi EMA Trend Following Trading Strategy" (EMA Trend Strategy).

FMZ source id: 474683

Source
    https://www.fmz.com/strategy/474683 (PineScript v5, FMZ last modified 2024-12-11 15:44:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-164), EMA 10 / 30 / 50
    up-trend and crossover(close, ema30) -> entry Buy;  crossunder(ema30, ema50) -> close Buy;  down-trend and crossunder(close, ema30) -> entry Sell;  crossover(ema30, ema50) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close coinciding with the opposite entry only repeats the reversal (#437773), so it is masked
      on entry bars; an entry and its own side's close cannot hold on one bar. REVERSAL INTENDED. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend re-crossings of the middle EMA with EMA-cross exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474683_ema10_30_50_trend_recross_ema30_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 5],
    "mid_len": [30, 20],
    "long_len": [50, 100],
}
DEFAULT_PARAMS = {"short_len": 10, "mid_len": 30, "long_len": 50}


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


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s, md, lg = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("short_len", "mid_len", "long_len"))
    le = (s > md) & (md > lg) & _x(c, md)
    se = (lg > md) & (md > s) & _x(md, c)
    lx = _x(lg, md) & ~se
    sx = _x(md, lg) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
