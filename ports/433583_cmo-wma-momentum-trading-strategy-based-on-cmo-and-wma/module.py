"""HPotter CMO against its WMA, broker days: a Chande-style momentum (9-bar change over 9 x the average absolute change)
above its WMA 9 turns the state long, at or below it short; always in.
Port of FMZ strategy #433583 "基于CMO和WMA的动量交易策略Momentum-Trading-Strategy-Based-on-CMO-and-WMA" (CMO & WMA).

FMZ source id: 433583

Source
    https://www.fmz.com/strategy/433583 (PineScript v2, FMZ last modified 2023-11-28 16:42:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 138-155), length 9, WMA 9, reverse false
    nRes = 100 (close - close[9]) / (sma(|close - close[1]|, 9) x 9);  pos = nRes > wma(nRes, 9) ? 1 : nRes <= wma ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * An undefined comparison keeps the state. strategy.entry reverses: REVERSAL INTENDED. reverse is
      false. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded momentum ratio against its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430117 (4 members, best partner #440005, Jaccard 0.726); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433583_cmo_vs_wma"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 18],
    "wma_len": [9, 18],
}
DEFAULT_PARAMS = {"length": 9, "wma_len": 9}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (w / w.sum())
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    res = 100 * (c - c.shift(n)) / (c.diff().abs().rolling(n).mean() * n)
    wm = _wma(res, int(p["wma_len"]))
    rv = res.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if rv[i] > wm[i]:
            pos = 1
        elif rv[i] <= wm[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
