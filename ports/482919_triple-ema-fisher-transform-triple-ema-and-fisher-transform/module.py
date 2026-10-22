"""Close crossings of TEMA 21 together with Fisher 10 crossing zero, broker days: both up on one bar goes long, both down goes short; either crossing back closes; reversing.
Port of FMZ strategy #482919 "Triple-EMA和Fisher-Transform趋势动量策略-Triple-EMA-and-Fisher-Transform-Trend-Momentum-Strategy" (Triple EMA (TEMA) + Fisher Transform Strategy).

FMZ source id: 482919

Source
    https://www.fmz.com/strategy/482919 (PineScript v5, FMZ last modified 2025-02-20 17:41:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-160), TEMA 21; Fisher 10 on hl2, smoothing 1; 10 % of equity
    value = clamp(0.5 (2 (hl2 - min10) / (max10 - min10) - 1), -0.999, 0.999);  fisher = 0.5 ln((1 + value) / (1 - value)) + 0.5 nz(fisher[1])
    crossover(close, tema) and crossover(fisher, 0) -> entry Long;  crossunder(close, tema) and crossunder(fisher, 0) -> entry Short
    crossunder(close, tema) or crossunder(fisher, 0) -> close Long;  crossover(close, tema) or crossover(fisher, 0) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Fisher value is not smoothed recursively (only the transform carries half its last value), as
      written; a flat 10-bar range gives na (Pine's division by zero) and the next bar reads it as 0
      through nz(). Smoothing 1 leaves it unchanged. A close on the bar of an entry is masked by the
      entry; an entry on the other side reverses (REVERSAL INTENDED). The 10 % of equity size is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TEMA crossings with Fisher zero crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482919_tema21_fisher10_zero_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tema_length": [21, 10],
    "fisher_length": [10, 20],
}
DEFAULT_PARAMS = {"tema_length": 21, "fisher_length": 10}


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
    n = int(p["tema_length"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    tema = 3 * e1 - 3 * e2 + e3
    pr = (h + lo) / 2
    k = int(p["fisher_length"])
    mx, mn = pr.rolling(k).max(), pr.rolling(k).min()
    rng = mx - mn
    v = (0.5 * (2 * ((pr - mn) / rng.where(rng != 0)) - 1)).clip(-0.999, 0.999).to_numpy(dtype=float)
    m = len(v)
    fv = np.full(m, np.nan)
    for i in range(m):
        prev = fv[i - 1] if i >= 1 and not np.isnan(fv[i - 1]) else 0.0
        if not np.isnan(v[i]):
            fv[i] = 0.5 * np.log((1 + v[i]) / (1 - v[i])) + 0.5 * prev
    f = pd.Series(fv, index=c.index)
    cu, cd = (c > tema) & (c.shift(1) <= tema.shift(1)), (c < tema) & (c.shift(1) >= tema.shift(1))
    fu, fd = (f > 0) & (f.shift(1) <= 0), (f < 0) & (f.shift(1) >= 0)
    le, se = cu & fu, cd & fd
    lx, sx = cd | fd, cu | fu
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
