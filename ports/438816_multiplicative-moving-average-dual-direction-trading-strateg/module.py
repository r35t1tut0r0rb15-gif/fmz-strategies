"""Profit Maximizer (PMax) crossings, broker days, long only: the EMA 10 of hl2 crossing over its ATR(10) x 3 PMax line buys, crossing under closes.
Port of FMZ strategy #438816 "Multiplicative Moving Average Dual direction Trading Strategy" (PMax-Strategy).

FMZ source id: 438816

Source
    https://www.fmz.com/strategy/438816 (PineScript v4, FMZ last modified 2024-01-15 14:50:32).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 173-287), source hl2; ATR 10 (Wilder) x 3; MA EMA 10; signal type crossing; long-short off; cash 10000
    longStop = MAvg - 3 atr, ratcheted while MAvg > longStop[1];  shortStop = MAvg + 3 atr, ratcheted;  dir flips on MAvg crossing the previous stops;  PMax = dir 1 ? longStop : shortStop
    crossover(MAvg, PMax) -> entry BUY;  long-short off: crossunder(MAvg, PMax) -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long-short is off, so the cross under only closes the long. The MA types other than EMA are not
      swept. Long only. The cash size and capital are sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average and ATR stop line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND365691 (3 members, best partner #365691, Jaccard 0.711); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438816_pmax_cross_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [3.0, 2.0],
    "length": [10, 20],
}
DEFAULT_PARAMS = {"multiplier": 3.0, "length": 10, "periods": 10}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["periods"])).to_numpy()
    mav = ((h + lo) / 2).ewm(span=int(p["length"]), adjust=False).mean().to_numpy()
    k = float(p["multiplier"])
    m = len(mav)
    ls, ss = np.full(m, np.nan), np.full(m, np.nan)
    pm = np.full(m, np.nan)
    d = 1
    for i in range(m):
        l0, s0 = mav[i] - k * atr[i], mav[i] + k * atr[i]
        lp = ls[i - 1] if i > 0 and not np.isnan(ls[i - 1]) else l0           # nz(longStop[1], longStop)
        sp = ss[i - 1] if i > 0 and not np.isnan(ss[i - 1]) else s0
        ls[i] = max(l0, lp) if (mav[i] > lp and not np.isnan(l0)) else l0
        ss[i] = min(s0, sp) if (mav[i] < sp and not np.isnan(s0)) else s0
        if d == -1 and mav[i] > sp:
            d = 1
        elif d == 1 and mav[i] < lp:
            d = -1
        pm[i] = ls[i] if d == 1 else ss[i]
    ms, ps = pd.Series(mav, index=c.index), pd.Series(pm, index=c.index)
    up = (ms > ps) & (ms.shift(1) <= ps.shift(1))
    dn = (ms < ps) & (ms.shift(1) >= ps.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
