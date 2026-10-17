"""Bollinger(10, 2) re-entries closed at the opposite band, daily (broker-day) bars: the close crossing back above the
lower band goes long, crossing back below the upper band goes short; a long closes on a bar whose high reaches the
upper band, a short on a bar whose low reaches the lower band.
Port of FMZ strategy #483048 "基于Bollinger带策略应用的动态出场交易系统-Dynamic-Exit-Trading-System-Based-on-Bollinger-Bands-Application" (Bollinger Strategy: Close at Band Touch v6).

FMZ source id: 483048

Source
    https://www.fmz.com/strategy/483048 (PineScript v6, FMZ last modified 2025-02-27 17:13:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 103-132), BB 10 x 2
    long = crossover(close, lower); short = crossunder(close, upper)
    position long and high >= upper -> close long; position short and low <= lower -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band-touch closes are bar-range checks acting through strategy.close: exit signals at the next open (rule 3;
      as #489638). They act on the position held at the bar's start and never undo that bar's entry (as #430850).
      Target-position state machine, exits only on going flat.
    * ta.stdev is the population standard deviation. Entries reverse (REVERSAL INTENDED). No stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; band-touch closes as exit signals.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1000 % of equity quoted in original_sizing.txt (sizing, not ported).
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

NAME = "fmz_483048_bollinger_reentry_band_touch_exit_1d"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 10, "mult": 2.0}


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
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    long_c = ((c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    short_c = ((c < upper) & (c.shift(1) >= upper.shift(1))).to_numpy()
    touch_up = (h >= upper).to_numpy()
    touch_dn = (lo <= lower).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if long_c[i]:
            pos = 1
        if short_c[i]:
            pos = -1
        if start == 1 and pos == 1 and touch_up[i]:
            pos = 0
        if start == -1 and pos == -1 and touch_dn[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
