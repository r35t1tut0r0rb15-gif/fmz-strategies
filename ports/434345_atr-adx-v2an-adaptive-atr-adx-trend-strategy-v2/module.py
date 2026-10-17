"""Adaptive ATR trailing trend line, broker days: the hl2 -/+ m x ATR 21 lines ratchet while the previous hlc3 and close stay
beyond them; m is 3.5 while the ADX 14 rises under 30 and 1.75 while it falls or is above 30. A flip of the trend to up
goes long, a flip to down goes short; always in the market after the first flip.
Port of FMZ strategy #434345 "自适应ATR-ADX趋势策略V2An-Adaptive-ATR-ADX-Trend-Strategy-V2" (Adaptive ATR-ADX Trend V2).

FMZ source id: 434345

Source
    https://www.fmz.com/strategy/434345 (PineScript v2, FMZ last modified 2023-12-05 18:08:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 158-227), source hlc3; ATR 21; multipliers 3.5 (ADX rising) / 1.75 (falling); ADX 14, threshold 30, above-threshold rule on; Heikin-Ashi off
    up = hl2 - mUp atr;  dn = hl2 + mDn atr;  TUp = max(hlc3[1], close[1]) > TUp[1] ? max(up, TUp[1]) : up;  TDown mirror
    trend = min(hlc3, close) > TDown[1] ? 1 : max(hlc3, close) < TUp[1] ? -1 : trend[1] (start 1)
    change(trend) > 0 -> entry long;  change(trend) < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DI / ADX use the author's running sums (x - x / 14 + new) and an SMA 14 of DX; m keeps its
      last value when the ADX is flat (0 before the first rule fires); mUp is m when DI+ >= DI- and
      1.75 otherwise, mDn the mirror. ATR is Wilder's ATR 21 (Heikin-Ashi off).
    * The trend line is the strategy's signal, checked on bar closes: a close-based reversal, not a
      broker stop (no mark). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR lines with an ADX-switched multiplier.
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

NAME = "fmz_434345_adaptive_atr_adx_trend"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "m1": [3.5, 2.5],
    "adx_thresh": [30, 20],
}
DEFAULT_PARAMS = {"atr_len": 21, "m1": 3.5, "m2": 1.75, "adx_len": 14, "adx_thresh": 30, "above_thresh": True}


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


def _running(x, n):
    """s = nz(s[1]) - nz(s[1]) / n + x (NaN where x is NaN)."""
    out = np.full(len(x), np.nan)
    s = 0.0
    for i in range(len(x)):
        if np.isnan(x[i]):
            s = 0.0
            continue
        s = s - s / n + x[i]
        out[i] = s
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    hr, lr = h.diff(), -lo.diff()
    dmp = np.where(hr > lr, np.maximum(hr, 0), 0.0)
    dmn = np.where(lr > hr, np.maximum(lr, 0), 0.0)
    na = int(p["adx_len"])
    s_tr = _running(tr.to_numpy(dtype=float), na)
    s_p, s_n = _running(dmp.astype(float), na), _running(dmn.astype(float), na)
    with np.errstate(invalid="ignore", divide="ignore"):
        dip = s_p / s_tr * 100
        din = s_n / s_tr * 100
        dx = np.abs(dip - din) / (dip + din) * 100
    adx = pd.Series(dx, index=c.index).rolling(na).mean().to_numpy()
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    m1, m2, th, ab = float(p["m1"]), float(p["m2"]), float(p["adx_thresh"]), bool(p["above_thresh"])
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    src = (hv + lv + cv) / 3
    t = (hv + lv) / 2
    n = len(cv)
    trend = np.ones(n, dtype=np.int8)
    mm, tu_p, td_p = 0.0, np.nan, np.nan
    for i in range(n):
        a0, a1 = adx[i], adx[i - 1] if i > 0 else np.nan
        rising, falling = a0 > a1, a0 < a1
        if rising and (a0 < th or not ab):
            mm = m1
        elif falling or (a0 > th and ab):
            mm = m2
        mup = mm if dip[i] >= din[i] else m2
        mdn = mm if din[i] >= dip[i] else m2
        up, dn = t[i] - mup * atr[i], t[i] + mdn * atr[i]
        if i > 0 and max(src[i - 1], cv[i - 1]) > tu_p:
            tu = np.nan if np.isnan(up) else max(up, tu_p)
        else:
            tu = up
        if i > 0 and min(src[i - 1], cv[i - 1]) < td_p:
            td = np.nan if np.isnan(dn) else min(dn, td_p)
        else:
            td = dn
        prev_tr = trend[i - 1] if i > 0 else 1
        if min(src[i], cv[i]) > td_p:
            trend[i] = 1
        elif max(src[i], cv[i]) < tu_p:
            trend[i] = -1
        else:
            trend[i] = prev_tr
        tu_p, td_p = tu, td
    t1 = np.concatenate(([trend[0]], trend[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series(trend > t1, index=ix), false, pd.Series(trend < t1, index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
