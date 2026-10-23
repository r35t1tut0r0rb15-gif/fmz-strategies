"""The close above its SMA 5 / 15 / 25 with volume over 1.8 times its SMA 30, ADX 20 over 15 with DI+ on top and a rising MESA-adaptive cloud line, broker days, long only: that state buys; a falling cloud line together with a down pivot-centre ATR trend closes.
Port of FMZ strategy #360018 "Get your trend" (Get your trend).

FMZ source id: 360018

Source
    https://www.fmz.com/strategy/360018 (PineScript v4, FMZ last modified 2022-05-07 13:52:58).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 46-256), SMA 5 / 15 / 25; pivot period 15, ATR factor 1 / period 1; ADX CLASSIC 20 > 15; cloud length 30 (MESA alpha from the efficiency ratio); volume x 1.8 over SMA 30
    Bulls = close above SMA 5, 15, 25 and volume > sma(volume, 30) x 1.8 and DI+ > DI- and ADX > 15 and not (kama < kama[1]) -> entry L
    close_all when kama < kama[1] and Trend == -1   (Trend: close vs a ratcheting pivot-centre +/- ATR(1) band, as SuperTrend)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud line is the source's KAMA: alpha = (er (b - a) + a)^2 from the MESA computeAlpha(src, er,
      er x 0.1) with er the 30-bar efficiency ratio, every history read through nz() as written (Pine
      function-local history, one call per bar). The trend band is centred on a running average of the
      15 / 15 pivots ((2 centre + pivot) / 3, the high pivot taken first on a bar with both), with
      ATR(1) = the true range, ratcheting as SuperTrend; Trend keeps its last value (1 at the start). The
      ADX is the CLASSIC menu default (the house DMI). The CondIni / average-price block is display only.
      Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA stack with volume, ADX and adaptive-cloud confirmation; trend-band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > sma(volume, 30) x 1.8; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_360018_sma_stack_volume_adx_mesa_cloud_pivot_trend_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "volume_f": [1.8, 1.2],
    "th": [15.0, 25.0],
}
DEFAULT_PARAMS = {"volume_f": 1.8, "th": 15.0, "length1": 5, "length2": 15, "length3": 25, "prd": 15,
                  "factor": 1.0, "pd_atr": 1, "adx_len": 20, "cloud_len": 30, "sma_length": 30}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def _pivot_value(x, side, span):
    """Pine pivothigh / pivotlow(span, span): the pivot's value at its confirmation bar, else NaN."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return x.shift(span).where((centre > left) & (centre > right))


def _nz(v):
    return 0.0 if np.isnan(v) else v


def _cloud(src, er):
    """The source's computeAlpha(src, er, er x 0.1) and its KAMA line, one call per bar, nz() as written."""
    s = src.to_numpy(dtype=float)
    e = er.to_numpy(dtype=float)
    m = len(s)
    sm, det, i1, q1 = (np.zeros(m) for _ in range(4))
    kama = np.full(m, np.nan)
    mp_p = i2_p = q2_p = re_p = im_p = ph_p = 0.0
    k_p = np.nan

    def g(a, j):
        return a[j] if j >= 0 else 0.0

    def hil(a, i):
        return 0.0962 * a[i] + 0.5769 * g(a, i - 2) - 0.5769 * g(a, i - 4) - 0.0962 * g(a, i - 6)

    for i in range(m):
        mult = 0.075 * mp_p + 0.54
        sm[i] = (4 * s[i] + 3 * g(s, i - 1) + 2 * g(s, i - 2) + g(s, i - 3)) / 10
        det[i] = hil(sm, i) * mult
        i1[i] = g(det, i - 3)
        q1[i] = hil(det, i) * mult
        ji, jq = hil(i1, i) * mult, hil(q1, i) * mult
        i2 = 0.2 * (i1[i] - jq) + 0.8 * i2_p
        q2 = 0.2 * (q1[i] + ji) + 0.8 * q2_p
        re = 0.2 * (i2 * i2_p + q2 * q2_p) + 0.8 * re_p
        im = 0.2 * (i2 * q2_p - q2 * i2_p) + 0.8 * im_p
        mp = 0.0
        if re != 0 and im != 0:
            mp = 2 * np.pi / np.arctan(im / re)
        if mp > 1.5 * mp_p:
            mp = 1.5 * mp_p
        if mp < 0.67 * mp_p:
            mp = 0.67 * mp_p
        mp = min(max(mp, 6.0), 50.0)
        mp = 0.2 * mp + 0.8 * mp_p
        ph = (180 / np.pi) * np.arctan(q1[i] / i1[i]) if i1[i] != 0 else 0.0
        dp = ph_p - ph
        if dp < 1:
            dp = 1.0
        a = e[i] / dp
        if a < e[i] * 0.1:
            a = e[i] * 0.1
        b = a / 2.0
        alpha = (e[i] * (b - a) + a) ** 2
        kama[i] = alpha * s[i] + (1 - alpha) * _nz(k_p)
        k_p = kama[i]
        mp_p, i2_p, q2_p, re_p, im_p, ph_p = mp, i2, q2, re, im, ph
    return pd.Series(kama, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    plus, minus, adx = _dmi(bars_df, int(p["adx_len"]))
    l_adx = (plus > minus) & (adx > float(p["th"]))
    prd = int(p["prd"])
    ph, pl = _pivot_value(h, 1, prd).to_numpy(dtype=float), _pivot_value(lo, -1, prd).to_numpy(dtype=float)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = (_rma(tr, int(p["pd_atr"])) * float(p["factor"])).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    trend = np.ones(m)
    centre = tup_p = tdn_p = np.nan
    t_p = np.nan
    for i in range(m):
        lastpp = ph[i] if (not np.isnan(ph[i]) and ph[i] != 0) else (pl[i] if (not np.isnan(pl[i]) and pl[i] != 0) else np.nan)
        if not np.isnan(lastpp):
            centre = lastpp if np.isnan(centre) else (centre * 2 + lastpp) / 3
        up, dn = centre - atr[i], centre + atr[i]
        cp = cv[i - 1] if i > 0 else np.nan
        tup = max(up, tup_p) if cp > tup_p else up
        tdn = min(dn, tdn_p) if cp < tdn_p else dn
        t = 1.0 if cv[i] > tdn_p else (-1.0 if cv[i] < tup_p else (1.0 if np.isnan(t_p) else t_p))
        trend[i] = t
        tup_p, tdn_p, t_p = tup, tdn, t
    s_atr = pd.Series(trend == -1, index=c.index)
    n = int(p["cloud_len"])
    er = (c - c.shift(n)).abs() / c.diff().abs().rolling(n).sum()
    kama = _cloud(c, er)
    s_cloud = kama < kama.shift(1)
    long_ma = (c.rolling(int(p["length1"])).mean() < c) & (c.rolling(int(p["length2"])).mean() < c) \
        & (c.rolling(int(p["length3"])).mean() < c)
    vol_ok = v > v.rolling(int(p["sma_length"])).mean() * float(p["volume_f"])
    le = long_ma & vol_ok & l_adx & ~s_cloud
    lx = s_cloud & s_atr
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
