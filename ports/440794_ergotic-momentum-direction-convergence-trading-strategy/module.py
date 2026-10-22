"""Ergotic TSI against its signal, broker days: the triple-smoothed TSI (4 / 8 / 6) above its EMA 3 signal goes long, below it short; reversing.
Port of FMZ strategy #440794 "Ergotic Momentum Direction Convergence Trading Strategy" (Ergotic TSI Strategy Backtest).

FMZ source id: 440794

Source
    https://www.fmz.com/strategy/440794 (PineScript v2, FMZ last modified 2024-02-02 10:51:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-168), r 4, s 8, u 6; signal 3; reverse off
    tsi = 100 ema(ema(ema(close - close[1], 4), 8), 6) / ema(ema(ema(|close - close[1]|, 4), 8), 6);  pos = tsi > ema(tsi, 3) ? 1 : tsi < ema(tsi, 3) ? -1 : previous;  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A zero denominator gives a TSI of 0, as written. The state is a level. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, triple-smoothed TSI.
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

NAME = "fmz_440794_ergotic_tsi_signal_daily"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "s": [8, 16],
    "smth_len": [3, 5],
}
DEFAULT_PARAMS = {"s": 8, "smth_len": 3, "r": 4, "u": 6, "reverse": False}


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
    d = c - c.shift(1)

    def e3(x):
        return x.ewm(span=int(p["r"]), adjust=False).mean().ewm(span=int(p["s"]), adjust=False).mean() \
            .ewm(span=int(p["u"]), adjust=False).mean()

    v1, v2 = 100 * e3(d), e3(d.abs())
    tsi = (v1 / v2.where(v2 != 0)).where(v2 != 0, 0.0).where(v2.notna())
    sig = tsi.ewm(span=int(p["smth_len"]), adjust=False).mean()
    up, dn = (tsi > sig).to_numpy(), (tsi < sig).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
