"""2/20 EMA and Bull And Bear Balance combination, broker days: both states long go long, both short go short, any disagreement closes all; reversing.
Port of FMZ strategy #438067 "Dual Moving Average Crossover and Bull Bear Power Balance Combination Strategy" (Combo).

FMZ source id: 438067

Source
    https://www.fmz.com/strategy/438067 (PineScript v5, FMZ last modified 2024-01-08 17:09:48).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 191-255), EMA length 14; Bull And Bear Balance sell level -15, buy level 15 (price units); reverse off; start 2005
    EMA20: nHH = max(high, high[1]), nLL = min(low, low[1]);  nXS = nLL if nLL > ema(14) or nHH < ema(14) else nHH;  pos = -1 if nXS > close[1], 1 if nXS < close[1], else pos[1]
    BBB: nBBB = value2 - value (the source's case tables);  pos = -1 if nBBB < -15, 1 if nBBB >= 15, else pos[1];  both 1 -> entry Long;  both -1 -> entry Short;  else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the balance levels are price units (15 USD on BTC); they become level_atr x the Wilder
      ATR 14 of the bar (about 0.015 ATR on daily BTC; as #430899). The case tables are ported line for
      line, close[1] compared with the current open as written. reverse is off; the 2005 start covers the
      data. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429466 (3 members, best partner #429466, Jaccard 0.732); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438067_ema2_20_bull_bear_balance_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "level_atr": [0.015, 0.25],
}
DEFAULT_PARAMS = {"length": 14, "level_atr": 0.015, "atr_len": 14, "reverse": False}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def _balance(o, h, lo, c, c1):
    """value2 - value of the source, bar by bar (c1 = close[1]; nan comparisons are false)."""
    if c < o:
        v = max(c - o, h - lo) if c1 > o else h - lo
        v2 = max(h - c1, c - lo) if c1 < o else max(h - o, c - lo)
    elif c > o:
        v = max(c1 - lo, h - c) if c1 > o else max(o - lo, h - c)
        v2 = h - lo if c1 > o else max(o - c1, h - lo)
    elif h - c > c - lo:
        v = max(c1 - o, h - lo) if c1 > o else h - lo
        v2 = max(h - c1, c - lo) if c1 < o else h - o
    elif h - c < c - lo:
        v = (max(c - lo, h - c) if c > o else o - lo)
        v2 = h - lo if c1 > o else max(o - c, h - lo)
    else:
        v = max(c1 - o, h - c) if c > o else (max(o - lo, h - c) if c1 < o else h - lo)
        v2 = max(h - o, c - lo) if c1 > o else (max(o - c, h - lo) if c1 < o else h - lo)
    return v2 - v


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1s = c.shift(1)
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    nhh = np.maximum(h, h.shift(1))
    nll = np.minimum(lo, lo.shift(1))
    nxs = np.where((nll > xa) | (nhh < xa), nll, nhh)
    tr = pd.concat([h - lo, (h - c1s).abs(), (lo - c1s).abs()], axis=1).max(axis=1)
    lvl = (_rma(tr, int(p["atr_len"])) * float(p["level_atr"])).to_numpy()
    ov, hv, lv, cv, c1 = (x.to_numpy(dtype=float) for x in (o, h, lo, c, c1s))
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pe = pb = 0
    for i in range(m):
        if nxs[i] > c1[i]:
            pe = -1
        elif nxs[i] < c1[i]:
            pe = 1
        b = _balance(ov[i], hv[i], lv[i], cv[i], c1[i])
        if b < -lvl[i]:
            pb = -1
        elif b >= lvl[i]:
            pb = 1
        tgt[i] = 1 if (pe == 1 and pb == 1) else (-1 if (pe == -1 and pb == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
