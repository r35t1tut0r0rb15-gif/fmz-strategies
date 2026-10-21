"""123 reversal and 2/20 EMA combination, broker days: the 123 reversal state and the 2/20 EMA state (EMA 20 band position against the previous close) agreeing long go long, agreeing short go short,
disagreeing close all; reversing.
Port of FMZ strategy #438787 "Dual Moving Average Reversal Trading Strategy" (Combo Backtest).

FMZ source id: 438787

Source
    https://www.fmz.com/strategy/438787 (PineScript v3, FMZ last modified 2024-01-15 12:35:29).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 160-196), 123: length 14, K smoothing 1, D 3, level 50; EMA length 20; reverse off
    EMA2_20: nXS = min(low, low[1]) if it or max(high, high[1]) is beyond ema(close, 20) on the outside, else max(high, high[1]);  pos = -1 if nXS > close[1], 1 if nXS < close[1], else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The states are levels, so the entry is sent on every bar of the
      agreement; disagreement closes. REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and EMA band position.
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

NAME = "fmz_438787_reversal123_ema2_20_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "ma_length": [20, 40],
}
DEFAULT_PARAMS = {"length": 14, "ma_length": 20, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "reverse": False}


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
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1s, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1s) & (c > c1s) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1s) & (c < c1s) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    xa = c.ewm(span=int(p["ma_length"]), adjust=False).mean()
    nhh = np.maximum(h, h.shift(1))
    nll = np.minimum(lo, lo.shift(1))
    nxs = np.where((nll > xa) | (nhh < xa), nll, nhh)
    c1 = c1s.to_numpy(dtype=float)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pe = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if nxs[i] > c1[i]:
            pe = -1
        elif nxs[i] < c1[i]:
            pe = 1
        tgt[i] = 1 if (p123 == 1 and pe == 1) else (-1 if (p123 == -1 and pe == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
