"""EMA 34 crosses, broker days: the EMA 34 crossing above the EMA 89 or the EMA 200 goes long, crossing below either goes
short.
Port of FMZ strategy #431287 "Crossing Moving Average Strategy" (EMA 34, 89, 200 e cruzamento das EMA).

FMZ source id: 431287

Source
    https://www.fmz.com/strategy/431287 (PineScript v3, FMZ last modified 2023-11-06 17:01:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 123-159), EMA 34 / 89 / 200
    crossover(ema34, ema200) -> entry "COMPRA FINAL";  crossover(ema34, ema89) -> entry "COMPRA INICIAL"
    crossunder(ema34, ema200) -> entry "VENDE FINAL";  crossunder(ema34, ema89) -> entry "VENDE INICIAL"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two long entries (and the two shorts) add nothing to each other at the default pyramiding
      of 1: one net position. A bar with both a long and a short cross takes the later short order,
      as Pine fills them in order. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

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
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431287_ema_34_89_200_crosses"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [34, 20],
    "mid": [89, 50],
}
DEFAULT_PARAMS = {"fast": 34, "mid": 89, "slow": 200}


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
    c = bars_df["close"]
    f, md, sl = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow"))

    def xo(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    lg = xo(f, sl) | xo(f, md)
    sh = xo(sl, f) | xo(md, f)
    m = len(lg)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lg[i]:
            pos = 1
        if sh[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
