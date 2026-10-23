"""Short-only trend entries, 30-minute bars: a down pivot-centre ATR trend with ADX 17 bearish (RSI 51 of highs not oversold), or an RSI 22 of the session VWAP crossing under 68 inside an up-trend context, sells short; an up-trend, an oversold RSI or the VWAP RSI crossing over 13 closes, with a 6 % stop from the entry.
Port of FMZ strategy #363564 "Welcome to the BEARMARKET 30MIN" (Welcome to the BEARMARKET [30MIN]).

FMZ source id: 363564

Source
    https://www.fmz.com/strategy/363564 (PineScript v4, FMZ last modified 2022-05-16 15:52:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 72-301), pivots 2 / 2, ATR factor 10 / period 14; cloud length 2 (MESA alpha); ADX CLASSIC 17 > 14; RSI 51 of high 70 / 30; RSI 22 of vwap(close) 13 / 68; stop 6 % of the avg price
    Short_condition = S_ATR and S_adx and not Os_rsi or S_VAP and not Os_rsi and L_cloud and L_ATR and L_adx -> entry S
    Short_close = L_ATR or Os_rsi or L_VAP -> close_all;  exit(qty_percent 100, loss = 6 % of the avg price in ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or": the second branch needs the VWAP RSI crossing under 68 with a rising cloud,
      an up-trend and a bullish ADX, as written. The trend band is the pivot-centre ATR line of #360018
      (factor 10, Wilder ATR 14); the cloud is the MESA KAMA of #360018 with length 2. vwap(close) is
      anchored at each broker-day start (BRIEF 1c; the source's session start). The 6 % loss is a ticks
      distance of 6 % of the average price: a fraction 0.06 of the fill, active from the fill (as
      #440797). An entry and a close on one bar: from flat the entry stands; a short held into the bar is
      closed (as #441963); the loop follows the stop on each bar's high (as #449508). The strategy() line
      is commented out; FMZ runs it with its defaults. Short only: Opposite entries cannot occur. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. The source carries the Mozilla Public
      License 2.0 notice. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 6 % stop from the fill.
    2 generic: PASS, trend-band / VWAP-RSI short entries with trend exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the commented strategy() line: fixed 1, capital 10000).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwap(close), anchored at the broker-day start; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start (17:00 America/New_York).
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363564_pivot_atr_trend_vwap_rsi_short_pct6_stop"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [10.0, 5.0],
    "stoploss": [6.0, 3.0],
}
DEFAULT_PARAMS = {"factor": 10.0, "stoploss": 6.0, "prd": 2, "pd_atr": 14, "cloud_len": 2, "adx_len": 17,
                  "th": 14.0, "len_3": 51, "rsi_vwap_length": 22}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


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


def _pivot_trend(bars_df, prd, factor, pd_atr):
    """The source's pivot-centre band: centre = (2 centre + pivot) / 3, band +/- factor x atr, SuperTrend ratchet."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ph = _pivot_value(h, 1, prd).to_numpy(dtype=float)
    pl = _pivot_value(lo, -1, prd).to_numpy(dtype=float)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = (_rma(tr, pd_atr) * factor).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    trend = np.ones(m)
    centre = tup_p = tdn_p = t_p = np.nan
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
    return trend


def _signals(bars_df, p):
    h, c, v = bars_df["high"], bars_df["close"], bars_df["volume"]
    trend = _pivot_trend(bars_df, int(p["prd"]), float(p["factor"]), int(p["pd_atr"]))
    l_atr, s_atr = trend == 1, trend == -1
    n = int(p["cloud_len"])
    er = (c - c.shift(n)).abs() / c.diff().abs().rolling(n).sum()
    kama = _cloud(c, er)
    l_cloud = (kama > kama.shift(1)).to_numpy()
    plus, minus, adx = _dmi(bars_df, int(p["adx_len"]))
    th = float(p["th"])
    l_adx = ((plus > minus) & (adx > th)).to_numpy()
    s_adx = ((plus < minus) & (adx > th)).to_numpy()
    d = h.diff()
    up3, dn3 = _rma(d.clip(lower=0), int(p["len_3"])), _rma((-d).clip(lower=0), int(p["len_3"]))
    rsi3 = (100 - 100 / (1 + up3 / dn3)).where(up3 != 0, 0.0).where(dn3 != 0, 100.0).where(up3.notna() & dn3.notna())
    os_rsi = (rsi3 <= 30).to_numpy()
    day = broker_day(c.index)
    pv = (c * v).groupby(day).cumsum()
    cv = v.groupby(day).cumsum()
    vwap = pd.Series((pv / cv.where(cv != 0)).to_numpy(), index=c.index)
    rv = _rsi(vwap, int(p["rsi_vwap_length"]))
    l_vap = ((rv > 13) & (rv.shift(1) <= 13)).to_numpy()
    s_vap = ((rv < 68) & (rv.shift(1) >= 68)).to_numpy()
    short_cond = (s_atr & s_adx & ~os_rsi) | (s_vap & ~os_rsi & l_cloud & l_atr & l_adx)
    short_close = l_atr | os_rsi | l_vap
    return short_cond, short_close


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sc, xc = _signals(bars_df, p)
    ov, hv = bars_df["open"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    k = float(p["stoploss"]) / 100
    m = len(ov)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, ent = 0, 0, np.nan
    for i in range(m):
        if pend == -1:
            pos, ent = -1, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == -1 and hv[i] >= ent * (1 + k):
            pos = 0                               # the 6 % stop fills inside this bar
        if pos == -1 and xc[i]:
            sx[i], pend = True, 2                 # close_all acts on the short held into the bar
        elif pos == 0 and sc[i]:
            se[i], pend = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stoploss"]) / 100}


def portfolio_kwargs(**params):
    return {}
