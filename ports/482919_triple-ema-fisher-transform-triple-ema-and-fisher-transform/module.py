"""Close crossing TEMA 21 on the same bar as the Fisher transform (10) crossing 0, closed when either crosses back,
daily (broker-day) bars: both crossing up goes long, both crossing down goes short; a long closes when the close crosses
below TEMA or the Fisher crosses below 0 (a short mirrored).
Port of FMZ strategy #482919 "Triple-EMA和Fisher-Transform趋势动量策略-Triple-EMA-and-Fisher-Transform-Trend-Momentum-Strategy" (Triple EMA (TEMA) + Fisher Transform Strategy).

FMZ source id: 482919

Source
    https://www.fmz.com/strategy/482919 (PineScript v5, FMZ last modified 2025-02-20 17:41:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-157), TEMA 21, Fisher 10, smoothing 1
    value = clamp(0.5 x (2 (hl2 - min) / (max - min) - 1), -0.999, 0.999) over 10 bars
    fisher = 0.5 ln((1 + value) / (1 - value)) + 0.5 nz(fisher[1])
    long = crossover(close, tema) and crossover(fisher, 0); short mirrored; exits as above; entries before closes

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Fisher value is not smoothed recursively (only the transform is), as written; smoothing 1 is off.
    * Closes act on the position held at the bar's start and never undo that bar's entry (as #430850). Target-position
      state machine, exits only on going flat. Entries reverse (REVERSAL INTENDED). No stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TEMA and a Fisher transform of the bar's range position.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482919_tema_fisher_joint_cross_1d"
FAMILY = "oscillator_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tema_len": [21, 34],
    "fisher_len": [10, 20],
}
DEFAULT_PARAMS = {"tema_len": 21, "fisher_len": 10}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["tema_len"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    tema = 3 * e1 - 3 * e2 + e3
    k = int(p["fisher_len"])
    price = (h + lo) / 2
    mx, mn = price.rolling(k).max(), price.rolling(k).min()
    val = (0.5 * (2 * ((price - mn) / (mx - mn)) - 1)).clip(-0.999, 0.999).to_numpy()
    fisher = np.full(len(val), np.nan)
    prev = np.nan
    for i, v in enumerate(val):
        f = 0.5 * np.log((1 + v) / (1 - v)) + 0.5 * (0.0 if np.isnan(prev) else prev)
        fisher[i] = f
        prev = f
    fs = pd.Series(fisher, index=c.index)
    cu = ((c > tema) & (c.shift(1) <= tema.shift(1))).to_numpy()
    cd = ((c < tema) & (c.shift(1) >= tema.shift(1))).to_numpy()
    fu = ((fs > 0) & (fs.shift(1) <= 0)).to_numpy()
    fd = ((fs < 0) & (fs.shift(1) >= 0)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if cu[i] and fu[i]:
            pos = 1
        if cd[i] and fd[i]:
            pos = -1
        if (cd[i] or fd[i]) and start == 1 and pos == 1:
            pos = 0
        if (cu[i] or fu[i]) and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
