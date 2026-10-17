"""EMA 50 crosses with signal-bar exits, broker days: the close crossing above the EMA 50 goes long and records that day's
high; the close crossing back under the recorded high closes the long. The mirror (cross under, the day's low recorded,
a close crossing back above it) runs the shorts.
Port of FMZ strategy #433094 "EMA Crossover Strategy" (EMA 50 Crossover Strategy).

FMZ source id: 433094

Source
    https://www.fmz.com/strategy/433094 (PineScript v5, FMZ last modified 2023-11-24 13:49:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-191), EMA 50
    crossover(close, ema50) -> longSignalHigh := high, entry long;  crossunder(close, ema50) -> shortSignalLow := low, entry short
    crossunder(close, longSignalHigh) -> close long;  crossover(close, shortSignalLow) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recorded levels are series (they change only on a signal bar), so the exit crosses compare
      the close with the level as it stood on the previous bar.
    * Each bar: the closes act on the position held at the start of the bar, then an entry wins (an
      entry against the position reverses it, as strategy.entry does).
    * REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses and signal-bar levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433094_ema_cross_signal_bar_exit"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [50, 20, 100],
}
DEFAULT_PARAMS = {"ema_len": 50}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = ((c > e) & (c.shift(1) <= e.shift(1))).to_numpy()
    se = ((c < e) & (c.shift(1) >= e.shift(1))).to_numpy()
    hv, lv, cv = h.to_numpy(), lo.to_numpy(), c.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    lsh = ssl = np.nan
    for i in range(m):
        lsh_prev, ssl_prev = lsh, ssl
        if le[i]:
            lsh = hv[i]
        if se[i]:
            ssl = lv[i]
        lx = i > 0 and cv[i] < lsh and cv[i - 1] >= lsh_prev
        sx = i > 0 and cv[i] > ssl and cv[i - 1] <= ssl_prev
        if pos == 1 and lx:
            pos = 0
        elif pos == -1 and sx:
            pos = 0
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
