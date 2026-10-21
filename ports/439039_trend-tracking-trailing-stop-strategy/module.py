"""Pivot-point SuperTrend with ADX, SMA and RSI filters, broker days, long only: a close above the pivot SuperTrend line, above the SMA 21, with the ADX 14 over 14 and the RSI 14 over 65 buys; a close under
the line closes.
Port of FMZ strategy #439039 "Trend Tracking Trailing Stop Strategy" (Bendre ADX Sup Trend).

FMZ source id: 439039

Source
    https://www.fmz.com/strategy/439039 (PineScript v5, FMZ last modified 2024-01-17 11:19:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 139-235), pivot period 2; ATR factor 2, ATR 18; ADX 14 (threshold 14); SMA 21; RSI 14 at 65; dates unused
    center = running blend of pivot highs / lows (center := (2 center + pivot) / 3);  Up / Dn = center -/+ 2 atr(18);  TUp / TDown ratcheted;  Trend flips on closes;  line = Trend 1 ? TUp : TDown
    buy = close > line and sma(close, 21) < close and ADX > 14;  buy and rsi > 65 -> entry Buy;  close < line and long -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivots are strict on both sides (as #434470) and confirmed 2 bars later; the latest pivot high
      wins over a pivot low on the same bar. The ADX is the source's own Wilder-style running sums (nz
      seeds; the first bar's true range uses a 0 previous close, as written), smoothed by an SMA 14. The
      date inputs feed no condition. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot SuperTrend line, ADX, SMA and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439039 (2 members, best partner #439642, Jaccard 0.860); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439039_pivot_supertrend_adx_rsi_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_factor": [2.0, 3.0],
    "over_bought": [65, 55],
}
DEFAULT_PARAMS = {"atr_factor": 2.0, "over_bought": 65.0, "pp_prd": 2, "atr_pd": 18, "len_adx": 14,
                  "th": 14.0, "len_ma": 21, "rsi_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _pivot_vals(x, k, low):
    """Pine pivothigh / pivotlow(k, k): the pivot value at bar i (pivot at i - k, strict both sides)."""
    m = len(x)
    out = np.full(m, np.nan)
    for i in range(2 * k, m):
        p = i - k
        w = np.concatenate((x[p - k:p], x[p + 1:i + 1]))
        if np.isnan(x[p]) or np.isnan(w).any():
            continue
        if (low and (x[p] < w).all()) or (not low and (x[p] > w).all()):
            out[i] = x[p]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = int(p["pp_prd"])
    ph, pl = _pivot_vals(hv, k, False), _pivot_vals(lv, k, True)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_pd"])).to_numpy()
    f = float(p["atr_factor"])
    m = len(cv)
    center = np.nan
    tu, td = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m)
    line = np.full(m, np.nan)
    for i in range(m):
        last = ph[i] if not np.isnan(ph[i]) else pl[i]
        if last > 0:
            center = last if np.isnan(center) else (center * 2 + last) / 3
        up_, dn_ = center - f * atr[i], center + f * atr[i]
        c1 = cv[i - 1] if i > 0 else np.nan
        tu1 = tu[i - 1] if i > 0 else np.nan
        td1 = td[i - 1] if i > 0 else np.nan
        tu[i] = max(up_, tu1) if (c1 > tu1 and not np.isnan(up_)) else up_
        td[i] = min(dn_, td1) if (c1 < td1 and not np.isnan(dn_)) else dn_
        prev = trend[i - 1] if i > 0 else 1.0
        trend[i] = 1.0 if cv[i] > td1 else (-1.0 if cv[i] < tu1 else prev)
        line[i] = tu[i] if trend[i] == 1 else td[i]
    n = int(p["len_adx"])
    h1 = np.concatenate(([0.0], hv[:-1]))
    l1 = np.concatenate(([0.0], lv[:-1]))
    cl1 = np.concatenate(([0.0], cv[:-1]))
    trr = np.maximum(np.maximum(hv - lv, np.abs(hv - cl1)), np.abs(lv - cl1))
    dmp = np.where(hv - h1 > l1 - lv, np.maximum(hv - h1, 0), 0.0)
    dmm = np.where(l1 - lv > hv - h1, np.maximum(l1 - lv, 0), 0.0)
    s_tr = s_p = s_m = 0.0
    dx = np.full(m, np.nan)
    for i in range(m):
        s_tr = s_tr - s_tr / n + trr[i]
        s_p = s_p - s_p / n + dmp[i]
        s_m = s_m - s_m / n + dmm[i]
        with np.errstate(divide="ignore", invalid="ignore"):
            dip, dim = s_p / s_tr * 100, s_m / s_tr * 100
            dx[i] = abs(dip - dim) / (dip + dim) * 100
    adx = pd.Series(dx, index=c.index).rolling(n).mean().to_numpy()
    sma = c.rolling(int(p["len_ma"])).mean().to_numpy()
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    buy = (cv > line) & (sma < cv) & (adx > float(p["th"])) & (rsi > float(p["over_bought"]))
    sell = cv < line
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0 and i + 1 < m:
            le[i], pos = True, 1
        elif sell[i] and pos == 1:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
