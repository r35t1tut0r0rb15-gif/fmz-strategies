"""HPotter absolute CMO bands, broker days: the absolute 9-bar momentum (as a share of the summed bar moves) above 70 reads short, below 20 reads long, the state holding between; reversing.
Port of FMZ strategy #442108 "Absolute Momentum Indicator Strategy" (CMOabs).

FMZ source id: 442108

Source
    https://www.fmz.com/strategy/442108 (PineScript v2, FMZ last modified 2024-02-19 14:13:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-184), length 9; top band 70; low band 20; reverse off
    nRes = |100 (close - close[9]) / (sma(|close - close[1]|, 9) x 9)|;  nRes > 70 -> -1, < 20 -> 1, else previous;  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is ported as written (high absolute momentum reads short). strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, absolute CMO bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430117 (4 members, best partner #430117, Jaccard 0.737); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442108_cmo_abs_band_state_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 14],
    "top_band": [70, 60],
}
DEFAULT_PARAMS = {"length": 9, "top_band": 70, "low_band": 20, "reverse": False}


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
    n = int(p["length"])
    den = c.diff().abs().rolling(n).mean() * n
    nres = (100 * (c - c.shift(n)) / den.where(den != 0)).abs()
    dn, up = (nres > float(p["top_band"])).to_numpy(), (nres < float(p["low_band"])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if dn[i]:
            pos = -1
        elif up[i]:
            pos = 1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
