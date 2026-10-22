"""Adaptive mean-deviation bands whose smoothing is the efficiency ratio since the first bar, daily bars, long only: a close above the mean plus the mean absolute deviation goes long, a close under the mean
minus it closes.
Port of FMZ strategy #446752 "Time Series Adaptive Dynamic Threshold Strategy Based on Equity Data" (EC (Equity control: efficiency-ratio adaptive bands)).

FMZ source id: 446752

Source
    https://www.fmz.com/strategy/446752 (PineScript v4, FMZ last modified 2024-04-01 10:48:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-147), source close; alpha = net move since the first bar / total path since the first bar
    er = |src - first src| / sum |src - src[1]|;  mean = (1 - er) mean[1] + er src;  dev = (1 - er) dev[1] + er |src - mean|
    src > mean + dev -> entry event (long);  src < mean - dev -> close event

Interpretation choices (Pine rules in SURVEY_README.md)
    * The efficiency ratio is measured from the data's first bar (var start), so it depends on where the
      data begins, as written. On the first bar the ratio is 0 / 0 (na), the mean starts at the close
      and the deviation at 0. The equity plot is display only. Long only. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the cumulative ratio uses past values only.
    2 generic: PASS, adaptive band breakout and breakdown.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446752_efficiency_ratio_adaptive_band_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    sv = bars_df["close"].to_numpy(dtype=float)
    m = len(sv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    start = sv[0] if m else np.nan
    total = 0.0
    mean = dev = np.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        for i in range(m):
            total += abs(sv[i] - (sv[i - 1] if i > 0 else sv[i]))
            a = abs(sv[i] - start) / total
            if np.isnan(mean):
                mean = sv[i]
            else:
                mean = (1 - a) * mean + a * sv[i]
            if np.isnan(dev):
                dev = 0.0
            else:
                dev = (1 - a) * dev + a * abs(sv[i] - mean)
            le[i] = sv[i] > mean + dev
            lx[i] = sv[i] < mean - dev
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
