"""Kaufman's gap momentum, broker days, long only: the ratio of the 40-day sum of up gaps (open over the previous close) to the sum of down gaps, smoothed by a 20-day SMA; while flat a rising signal goes long, while
long a falling signal closes it.
Port of FMZ strategy #436872 "Momentum Gap Trading Strategy" (TASC 2024.01 Gap Momentum System).

FMZ source id: 436872

Source
    https://www.fmz.com/strategy/436872 (PineScript v5, FMZ last modified 2023-12-28 14:38:33).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 235-263), period 40, signal 20, long only on
    gap = open - close[1];  gapsUp / gapsDn = sum over 40 bars of the up / down gaps;  gapRatio = gapsDn == 0 ? 1 : 100 gapsUp / gapsDn;  signal = sma(gapRatio, 20)
    opentrades <= 0 and signal > signal[1] -> entry long;  else opentrades > 0 and signal < signal[1] -> close_all (long only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The gap is the broker day's first-minute open against the previous broker day's last close. The
      ratio of two sums of the same price gaps is scale-free. The short branch is off by default (long only)
      and not ported. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ratio of gap sums.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the gap is between broker days; no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436872_gap_momentum_long_only"
FAMILY = "momentum_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [40, 20],
    "signal_period": [20, 10],
}
DEFAULT_PARAMS = {"period": 40, "signal_period": 20}


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
    o, c = bars_df["open"], bars_df["close"]
    gap = o - c.shift(1)
    gu = gap.where(gap > 0, 0.0)
    gd = (-gap).where(gap < 0, 0.0)
    n = int(p["period"])
    su, sd = gu.rolling(n).sum(), gd.rolling(n).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (100.0 * su / sd).where(sd != 0, 1.0).where(sd.notna())
    sig = ratio.rolling(int(p["signal_period"])).mean()
    rise = (sig > sig.shift(1)).to_numpy()
    fall = (sig < sig.shift(1)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and rise[i]:
            le[i] = True
            pos = 1
        elif pos == 1 and fall[i]:
            lx[i] = True
            pos = 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
