"""2/20 EMA and Accelerator Oscillator combination, broker days: both states long go long, both short go short, any disagreement closes all; reversing.
Port of FMZ strategy #438775 "基于双EMA和AC指标的趋势跟踪策略Dual-EMA-and-AC-Indicator-Based-Trend-Following-Strategy" (Combo).

FMZ source id: 438775

Source
    https://www.fmz.com/strategy/438775 (PineScript v5, FMZ last modified 2024-01-15 12:02:54).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 195-243), EMA length 14; AC slow 33, fast 6; reverse off; start 2005
    EMA20: nXS = min(low, low[1]) if it or max(high, high[1]) is beyond ema(14) on the outside, else max(high, high[1]);  pos = -1 if nXS > close[1], 1 if nXS < close[1], else pos[1]
    AC: ao = sma(hl2, 6) - sma(hl2, 33);  nRes = ao - sma(ao, 6);  pos = -1 if nRes < 0, 1 if nRes > 0, else pos[1];  both 1 -> entry Long;  both -1 -> entry Short;  else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * reverse is off; the 2005 start covers the data. The states are levels, so the entry is sent on
      every bar of the agreement; disagreement closes. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA band position and accelerator oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430896 (2 members, best partner #430896, Jaccard 0.668); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438775_ema2_20_accelerator_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "slow": [33, 21],
}
DEFAULT_PARAMS = {"length": 14, "slow": 33, "fast": 6, "reverse": False}


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
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    nhh = np.maximum(h, h.shift(1))
    nll = np.minimum(lo, lo.shift(1))
    nxs = np.where((nll > xa) | (nhh < xa), nll, nhh)
    hl2 = (h + lo) / 2
    f = int(p["fast"])
    ao = hl2.rolling(f).mean() - hl2.rolling(int(p["slow"])).mean()
    ac = (ao - ao.rolling(f).mean()).to_numpy()
    c1 = c.shift(1).to_numpy(dtype=float)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pe = pa = 0
    for i in range(m):
        if nxs[i] > c1[i]:
            pe = -1
        elif nxs[i] < c1[i]:
            pe = 1
        if ac[i] < 0:
            pa = -1
        elif ac[i] > 0:
            pa = 1
        tgt[i] = 1 if (pe == 1 and pa == 1) else (-1 if (pe == -1 and pa == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
