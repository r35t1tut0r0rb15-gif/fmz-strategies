"""Pivot-point SuperTrend with an ADX and SMA 21 filter, broker days, long only: the close above the pivot SuperTrend line (pivots 2 / 2, ATR 20 x 5) with the close above the SMA 21 and the ADX over 25
goes long; the close under the line sells the long.
Port of FMZ strategy #442120 "基于超趋势支撑阻力与ADX指标的高频交易策ADX-Filtered-SuperTrend-Pivot-Trading-Strategy" (STPP20 + ADX).

FMZ source id: 442120

Source
    https://www.fmz.com/strategy/442120 (PineScript v4, FMZ last modified 2024-02-19 15:01:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-237), pivot period 2; ATR factor 5, period 20; ADX 14 (25); SMA 21
    center = first pivot, then (center 2 + pivot) / 3;  Up / Dn = center -+ 5 atr(20);  TUp / TDown ratchet on close[1];  Trend = close > TDown[1] ? 1 : close < TUp[1] ? -1 : Trend[1];  line = Trend == 1 ? TUp : TDown
    ADX = sma(DX, 14) with nz-seeded Wilder sums;  buy = close > line and sma21 < close and ADX > 25 -> entry Buy;  close < line and long -> strategy.order("Sell", sell, default qty)

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow (2, 2) are confirmed 2 bars after their centre (past bars only), strict on both
      sides. The ADX follows the script's nz-seeded Wilder sums. The sell is strategy.order with the
      default quantity, the same as the entry's, so it closes the long. Long only. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot SuperTrend, ADX and SMA filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the sell order uses the default quantity).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442120_pivot_supertrend_adx_sma21_long"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pp_prd": [2, 3],
    "atr_factor": [5.0, 3.0],
}
DEFAULT_PARAMS = {"pp_prd": 2, "atr_factor": 5.0, "atr_pd": 20, "len_adx": 14, "adx_th": 25, "len_ma": 21}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pp = int(p["pp_prd"])
    ph = _pivot(h, pp, pp, True).to_numpy()
    pl = _pivot(lo, pp, pp, False).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_pd"])).to_numpy()
    fac = float(p["atr_factor"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    center = np.nan
    tu = tdn = np.nan
    trend = 1
    for i in range(m):
        lp = ph[i] if not np.isnan(ph[i]) and ph[i] != 0 else (pl[i] if not np.isnan(pl[i]) and pl[i] != 0 else np.nan)
        if not np.isnan(lp):
            center = lp if np.isnan(center) else (center * 2 + lp) / 3
        up_b, dn_b = center - fac * atr[i], center + fac * atr[i]
        cp = cv[i - 1] if i > 0 else np.nan
        ntu = (np.nan if np.isnan(up_b) else max(up_b, tu)) if cp > tu else up_b
        ntd = (np.nan if np.isnan(dn_b) else min(dn_b, tdn)) if cp < tdn else dn_b
        trend = 1 if cv[i] > tdn else (-1 if cv[i] < tu else trend)
        line[i] = ntu if trend == 1 else ntd
        tu, tdn = ntu, ntd
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    la = int(p["len_adx"])
    s_tr = s_p = s_m = 0.0
    adx_dx = np.full(m, np.nan)
    for i in range(m):
        c1 = cv[i - 1] if i > 0 else 0.0
        h1 = hv[i - 1] if i > 0 else 0.0
        l1 = lv[i - 1] if i > 0 else 0.0
        trv = max(max(hv[i] - lv[i], abs(hv[i] - c1)), abs(lv[i] - c1))
        dmp = max(hv[i] - h1, 0) if hv[i] - h1 > l1 - lv[i] else 0.0
        dmm = max(l1 - lv[i], 0) if l1 - lv[i] > hv[i] - h1 else 0.0
        s_tr = s_tr - s_tr / la + trv
        s_p = s_p - s_p / la + dmp
        s_m = s_m - s_m / la + dmm
        dip, dim = s_p / s_tr * 100, s_m / s_tr * 100
        adx_dx[i] = abs(dip - dim) / (dip + dim) * 100 if (dip + dim) != 0 else np.nan
    adx = pd.Series(adx_dx, index=c.index).rolling(la).mean()
    ln = pd.Series(line, index=c.index)
    buy = ((c > ln) & (c.rolling(int(p["len_ma"])).mean() < c) & (adx > float(p["adx_th"]))).to_numpy()
    sell = (c < ln).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0
    for i in range(m):
        if held == 0 and buy[i] and i + 1 < m:
            le[i], held = True, 1
        elif held == 1 and sell[i]:
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
