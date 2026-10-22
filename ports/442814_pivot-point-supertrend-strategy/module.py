"""Pivot Point SuperTrend flips or classic SuperTrend(10, 3) flips with an SMA 20 filter, daily bars: either trend turning up (the classic one with the close above the SMA) goes long, turning down goes
short; reversing.
Port of FMZ strategy #442814 "Pivot Point SuperTrend Strategy" (PPS (Pivot Point SuperTrend)).

FMZ source id: 442814

Source
    https://www.fmz.com/strategy/442814 (PineScript v4, FMZ last modified 2024-02-26 10:57:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-270), pivot period 2; ATR factor 3, period 10 (pivot line); SuperTrend ATR 10 x 3 on hl2 (Wilder ATR); SMA 20; dates from Sep 2018 (dropped); cash 50000 per trade, capital 500000
    center = weighted mean of the confirmed pivots (center 2/3 + pivot 1/3);  TUp / TDown = center -+ 3 atr(10) ratcheted;  Trend = close > TDown[1] ? 1 : close < TUp[1] ? -1 : prev
    trend (classic SuperTrend 10 x 3);  long = (trend flips up and close > sma20) or pivot Trend flips up;  short = (trend flips down and close < sma20) or pivot Trend flips down
    long -> entry BUY;  short -> close BUY, entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow(2, 2) are confirmed two bars after the pivot, as Pine returns them. The
      pivot centre starts at the first pivot. Both trend lines follow the script's na / nz seeds. When
      both signals fire on one bar the later short wins (as #437773). The date window is dropped.
      strategy.entry reverses: REVERSAL INTENDED. The cash size and capital are sizing. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots used once confirmed.
    2 generic: PASS, pivot SuperTrend and classic SuperTrend flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442814_pivot_point_supertrend_flip_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "prd": [2, 5],
}
DEFAULT_PARAMS = {"factor": 3.0, "prd": 2, "atr_pd": 10, "periods": 10, "ma_len": 20}


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


def _pivot(x, left, right, high):
    """Pine pivothigh / pivotlow (strict), the centre's value on the bar it is confirmed (right bars later)."""
    c = x.shift(right)
    ok = c.notna()
    for k in range(1, left + 1):
        ok &= (c > x.shift(right + k)) if high else (c < x.shift(right + k))
    for k in range(right):
        ok &= (c > x.shift(k)) if high else (c < x.shift(k))
    return c.where(ok)


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    f, prd = float(p["factor"]), int(p["prd"])
    ph = _pivot(h, prd, prd, True).to_numpy()
    pl = _pivot(lo, prd, prd, False).to_numpy()
    a1 = _rma(tr, int(p["atr_pd"])).to_numpy()
    a2 = _rma(tr, int(p["periods"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    ma = c.rolling(int(p["ma_len"])).mean().to_numpy()
    m = len(cv)
    pt = np.zeros(m, dtype=np.int8)
    st = np.zeros(m, dtype=np.int8)
    center = np.nan
    tup_p = tdn_p = np.nan
    trend_p = 1
    up_p = dn_p = np.nan
    d = 1
    for i in range(m):
        lp = ph[i] if (not np.isnan(ph[i]) and ph[i] != 0) else (pl[i] if (not np.isnan(pl[i]) and pl[i] != 0) else np.nan)
        if not np.isnan(lp):
            center = lp if np.isnan(center) else (center * 2 + lp) / 3
        up_c, dn_c = center - f * a1[i], center + f * a1[i]
        tup = _nmax(up_c, tup_p) if (i > 0 and cv[i - 1] > tup_p) else up_c
        tdn = _nmin(dn_c, tdn_p) if (i > 0 and cv[i - 1] < tdn_p) else dn_c
        if cv[i] > tdn_p:
            trend = 1
        elif cv[i] < tup_p:
            trend = -1
        else:
            trend = trend_p
        pt[i] = trend
        tup_p, tdn_p, trend_p = tup, tdn, trend
        # the classic SuperTrend block (nz seeds)
        u, dd = hl2[i] - f * a2[i], hl2[i] + f * a2[i]
        u1 = u if np.isnan(up_p) else up_p
        d1 = dd if np.isnan(dn_p) else dn_p
        if i > 0 and cv[i - 1] > u1:
            u = _nmax(u, u1) if not np.isnan(u) else u
        if i > 0 and cv[i - 1] < d1:
            dd = _nmin(dd, d1) if not np.isnan(dd) else dd
        if d == -1 and cv[i] > d1:
            d = 1
        elif d == 1 and cv[i] < u1:
            d = -1
        st[i] = d
        up_p, dn_p = u, dd
    pt1 = np.concatenate(([1], pt[:-1]))
    st1 = np.concatenate(([1], st[:-1]))
    with np.errstate(invalid="ignore"):
        lg = ((st == 1) & (st1 == -1) & (cv > ma)) | ((pt == 1) & (pt1 == -1))
        sh = ((st == -1) & (st1 == 1) & (cv < ma)) | ((pt == -1) & (pt1 == 1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lg & ~sh, index=ix), false, pd.Series(sh, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
