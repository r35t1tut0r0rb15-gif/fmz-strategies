"""MACD 12 / 26 / 20 histogram zero crossings, broker days: up through zero goes long, down through zero goes short; the histogram rising through +11 (read as a fraction of the close) closes a long, falling through -9 closes a short; reversing.
Port of FMZ strategy #483794 "Multi Indicator Momentum Wave Trading Strategy" (Neon Momentum Waves Strategy).

FMZ source id: 483794

Source
    https://www.fmz.com/strategy/483794 (PineScript v5, FMZ last modified 2025-02-26 10:30:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 273-329), MACD 12 / 26, signal 20; entry level 0; long exit 11; short exit -9; capital 100000
    crossover(hist, 0) -> entry Long;  crossunder(hist, 0) -> entry Short
    long and crossover(hist, 11) -> close Long;  short and crossunder(hist, -9) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the exit levels 11 and -9 are price amounts of the histogram; read at the header's
      ETH_USDT prices (about 3000) as 3.667e-03 and -3.0e-03 of the close (as #440456 reads price units).
      A close on the bar of an entry is masked by the entry; an entry on the other side reverses
      (REVERSAL INTENDED). The capital is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, histogram exit levels read as fractions of the close at ETH 3000.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital stored, not ported.
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

NAME = "fmz_483794_macd12_26_20_hist_zero_cross_level_exit_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "signal_length": [20, 9],
    "long_exit_frac": [3.667e-03, 6.0e-03],
}
DEFAULT_PARAMS = {"signal_length": 20, "long_exit_frac": 3.667e-03, "short_exit_frac": -3.0e-03, "fast_length": 12,
                  "slow_length": 26}


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

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["fast_length"]) - ema(c, p["slow_length"])
    hist = macd - ema(macd, p["signal_length"])
    le = (hist > 0) & (hist.shift(1) <= 0)
    se = (hist < 0) & (hist.shift(1) >= 0)
    lu = float(p["long_exit_frac"]) * c
    sd = float(p["short_exit_frac"]) * c
    lx = (hist > lu) & (hist.shift(1) <= lu.shift(1))
    sx = (hist < sd) & (hist.shift(1) >= sd.shift(1))
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
