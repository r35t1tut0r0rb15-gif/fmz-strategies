"""123 reversal and daily pivot-point combination, 1-hour bars: the 123 reversal state and the pivot state (a close above the previous day's R1: long; under its S1: short) agreeing long go long, agreeing
short go short, disagreeing close all; reversing.
Port of FMZ strategy #438951 "Combination Strategy of 123 Reversal and Pivot Point" (Combo).

FMZ source id: 438951

Source
    https://www.fmz.com/strategy/438951 (PineScript v4, FMZ last modified 2024-01-16 15:48:44).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 145-198), 123: length 14, K smoothing 1, D 3, level 50; pivot resolution D, sell from R1, buy from S1; reverse off
    PP2: H / L / C = security(tickerid, D, high / low / close);  PP = (H + L + C) / 3, R1 = 2 PP - L, S1 = 2 PP - H;  pos = 1 if close > R1, -1 if close < S1, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar: the previous
      broker day's high, low and close, built from the module's own bars. The 123 test is read as
      written. The states are levels; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily levels from completed days.
    2 generic: PASS, close patterns, stochastic and floor pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily levels.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438951_reversal123_daily_pivot_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "level_set": [1, 2],
}
DEFAULT_PARAMS = {"length": 14, "level_set": 1, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "reverse": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    day = broker_day(bars_df.index)
    d = bars_df.groupby(day).agg({"high": "max", "low": "min", "close": "last"}).shift(1)
    dh = d["high"].reindex(day).to_numpy()                  # last completed day
    dl = d["low"].reindex(day).to_numpy()
    dc = d["close"].reindex(day).to_numpy()
    pp = (dh + dl + dc) / 3
    r1, s1 = 2 * pp - dl, 2 * pp - dh
    if int(p["level_set"]) == 2:
        rb, sb = pp + (r1 - s1), pp - (r1 - s1)
    else:
        rb, sb = r1, s1
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = ppv = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if cv[i] > rb[i]:
            ppv = 1
        elif cv[i] < sb[i]:
            ppv = -1
        tgt[i] = 1 if (p123 == 1 and ppv == 1) else (-1 if (p123 == -1 and ppv == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
