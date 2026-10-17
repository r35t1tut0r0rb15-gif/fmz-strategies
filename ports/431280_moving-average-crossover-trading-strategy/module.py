"""EMA crosses of the typical price (TwoChiefs), broker days, long only: the EMA 13 of hlc3 crossing above its EMA 48 goes
long; the close crossing under the EMA 30 of hlc3 closes the long.
Port of FMZ strategy #431280 "Moving Average Crossover Trading Strategy" (John EMA Crossover Strategy).

FMZ source id: 431280

Source
    https://www.fmz.com/strategy/431280 (PineScript v4, FMZ last modified 2023-11-06 16:38:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 182-268), EMA 13 / 48 / 30 of hlc3
    buy = crossover(ema(hlc3, 13), ema(hlc3, 48)) -> entry long;  exit = crossunder(close, ema(hlc3, 30)) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default smoothing type EMA for all three averages (VWMA and the others are options, off by
      default). time_cond is always true. The close is written after the entry and acts on the
      position held at the bar's start. Long only; Opposite entries cannot occur. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431280_hlc3_ema_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_len": [48, 100],
    "exit_len": [30, 15],
}
DEFAULT_PARAMS = {"short_len": 13, "long_len": 48, "exit_len": 30}


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
    piv = (h + lo + c) / 3
    s = piv.ewm(span=int(p["short_len"]), adjust=False).mean()
    lg = piv.ewm(span=int(p["long_len"]), adjust=False).mean()
    ex = piv.ewm(span=int(p["exit_len"]), adjust=False).mean()
    buy = ((s > lg) & (s.shift(1) <= lg.shift(1))).to_numpy()
    out = ((c < ex) & (c.shift(1) >= ex.shift(1))).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if start == 1 and out[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
