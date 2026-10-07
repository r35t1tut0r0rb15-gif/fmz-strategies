"""SMA BTC killer: close above SMA 14/28/55 with a strong ADX (+DI > -DI, ADX > 21) and a rising
MAMA-adaptive KAMA goes long (the mirror short); a flip of the pivot-centre ATR trend against
the last signalled side closes everything.
Port of FMZ strategy #363766 "Sma BTC killer".

Source
    https://www.fmz.com/strategy/363766 (PineScript v4, FMZ last modified 2022-05-17 13:41:03).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 97-307), SMA 14/28/55, ADX "MASANAKAMURA" 29 (> 21),
cloud length 11, pivot period 18, ATR factor 5 / period 6
    ADX: Wilder-style running sums of TR, +DM, -DM (nz on the first bar); ADX = sma(DX, 29)
    er = |change(close, 11)| / sum(|change(close)|, 11); [a, b] = MAMA alpha(close, er, er/10)
    kama := (er*(b - a) + a)^2 * close + (1 - ...) * nz(kama[1]);  L_cloud = kama rising
    center = running mean of pivot highs/lows (2:1 weights); Up/Dn = center -+ 5 * atr(6)
    Trend flips on close beyond the trailing Dn/Up; bsignal / ssignal = flips
    Long_MA  = L_adx and L_cloud and close above all three SMAs -> entry long
    Short_MA = mirror -> entry short
    close_all when (ssignal and last signalled side long) or (bsignal and last side short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Last signalled side" is the author's in_longCondition: the later of the bars where
      Long_MA[1] / Short_MA[1] first held after the other side (CondIni logic).
    * Same-bar entry and close_all: Pine fills the entry first and then closes; the result is
      flat if a position existed, so the port emits only the exit then. From flat the entry
      stands.
    * The MAMA phase/period recursion is reproduced as coded (including its nz() seeds).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header (exchange in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363766_sma_adx_kama_pivot_trend"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_len": [14, 29],
    "adx_th": [21, 25],
    "cloud_len": [11, 20],
}
DEFAULT_PARAMS = {"sma1": 14, "sma2": 28, "sma3": 55, "adx_len": 29, "adx_th": 21, "cloud_len": 11,
                  "pp_period": 18, "atr_factor": 5.0, "atr_period": 6}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _pivots(x, left, right, high):
    """ta.pivothigh/pivotlow(x, left, right): value of the pivot confirmed on each bar (NaN if
    none); the centre bar t-right strictly beyond the `left` bars before and `right` bars after."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for t in range(left + right, len(v)):
        c = t - right
        side = np.concatenate([v[c - left:c], v[c + 1:t + 1]])
        if np.isnan(v[c]) or np.isnan(side).any():
            continue
        if (high and v[c] > side.max()) or (not high and v[c] < side.min()):
            out[t] = v[c]
    return out


def _nz(x):
    return 0.0 if np.isnan(x) else x


def _adx_masanakamura(h, l, c, n):
    m = len(c)
    dip, dim = np.full(m, np.nan), np.full(m, np.nan)
    s_tr = s_p = s_m = np.float64(0.0)  # numpy division: 0 -> inf/nan, as Pine
    for i in range(m):
        pc, ph, pl = (c[i - 1], h[i - 1], l[i - 1]) if i else (0.0, 0.0, 0.0)
        tr = max(h[i] - l[i], abs(h[i] - pc), abs(l[i] - pc))
        dmp = max(h[i] - ph, 0.0) if h[i] - ph > pl - l[i] else 0.0
        dmm = max(pl - l[i], 0.0) if pl - l[i] > h[i] - ph else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        dip[i], dim[i] = s_p / s_tr * 100, s_m / s_tr * 100
    dx = pd.Series(np.abs(dip - dim) / (dip + dim) * 100)
    return dip, dim, dx.rolling(n).mean().to_numpy()


def _ht(x, i):
    g = lambda k: _nz(x[i - k]) if i - k >= 0 else 0.0
    return 0.0962 * x[i] + 0.5769 * g(2) - 0.5769 * g(4) - 0.0962 * g(6)


def _mama_alpha(src, fast, slow):
    m = len(src)
    smooth, det, i1, q1, ji, jq = (np.full(m, np.nan) for _ in range(6))
    i2 = q2 = re = im = mp = phase = 0.0
    a_out = np.full(m, np.nan)
    for i in range(m):
        mult = 0.075 * mp + 0.54
        g = lambda k: _nz(src[i - k]) if i - k >= 0 else 0.0
        smooth[i] = (4 * src[i] + 3 * g(1) + 2 * g(2) + g(3)) / 10
        det[i] = _ht(smooth, i) * mult
        i1[i] = _nz(det[i - 3]) if i >= 3 else 0.0
        q1[i] = _ht(det, i) * mult
        ji[i] = _ht(i1, i) * mult
        jq[i] = _ht(q1, i) * mult
        i2_new = 0.2 * (i1[i] - jq[i]) + 0.8 * _nz(i2)
        q2_new = 0.2 * (q1[i] + ji[i]) + 0.8 * _nz(q2)
        re_new = 0.2 * (i2_new * _nz(i2) + q2_new * _nz(q2)) + 0.8 * _nz(re)
        im_new = 0.2 * (i2_new * _nz(q2) - q2_new * _nz(i2)) + 0.8 * _nz(im)
        i2, q2, re, im = i2_new, q2_new, re_new, im_new
        mp_prev = _nz(mp)
        p = 0.0
        if re != 0 and im != 0:
            p = 2 * np.pi / np.arctan(im / re)
        if p > 1.5 * mp_prev:
            p = 1.5 * mp_prev
        if p < 0.67 * mp_prev:
            p = 0.67 * mp_prev
        p = min(max(p, 6.0), 50.0)
        mp = 0.2 * p + 0.8 * mp_prev
        ph = (180 / np.pi) * np.arctan(q1[i] / i1[i]) if i1[i] != 0 else 0.0
        dp = max(_nz(phase) - ph, 1.0)
        phase = ph
        alpha = fast[i] / dp
        a_out[i] = slow[i] if alpha < slow[i] else alpha
    return a_out


def _pivot_trend(bars, prd, factor, atr_p):
    h, l, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    ph = _pivots(bars["high"], prd, prd, True)
    pl = _pivots(bars["low"], prd, prd, False)
    atr = _atr_pine(bars, atr_p).to_numpy()
    m = len(c)
    trend = np.zeros(m)
    center = np.nan
    t_up = t_dn = np.nan
    for i in range(m):
        last = ph[i] if not np.isnan(ph[i]) and ph[i] != 0 else (pl[i] if not np.isnan(pl[i]) and pl[i] != 0 else np.nan)
        if not np.isnan(last):
            center = last if np.isnan(center) else (center * 2 + last) / 3
        up, dn = center - factor * atr[i], center + factor * atr[i]
        new_up = max(up, t_up) if i and c[i - 1] > t_up else up
        new_dn = min(dn, t_dn) if i and c[i - 1] < t_dn else dn
        prev = trend[i - 1] if i else 1.0
        trend[i] = 1.0 if c[i] > t_dn else (-1.0 if c[i] < t_up else prev)
        t_up, t_dn = new_up, new_dn
    return trend


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    cs = bars_df["close"]
    above = np.ones(len(c), dtype=bool)
    below = np.ones(len(c), dtype=bool)
    for k in ("sma1", "sma2", "sma3"):
        s = cs.rolling(int(p[k])).mean().to_numpy()
        above &= s < c
        below &= s > c
    dip, dim, adx = _adx_masanakamura(h, l, c, int(p["adx_len"]))
    l_adx = (dip > dim) & (adx > p["adx_th"])
    s_adx = (dip < dim) & (adx > p["adx_th"])
    n = int(p["cloud_len"])
    er = ((cs - cs.shift(n)).abs() / cs.diff().abs().rolling(n).sum()).to_numpy()
    a = _mama_alpha(c, er, er * 0.1)
    b = a / 2.0
    alpha = (er * (b - a) + a) ** 2
    kama = np.full(len(c), np.nan)
    for i in range(len(c)):
        kama[i] = alpha[i] * c[i] + (1 - alpha[i]) * (_nz(kama[i - 1]) if i else 0.0)
    kprev = np.concatenate([[np.nan], kama[:-1]])
    long_ma = l_adx & (kama > kprev) & above
    short_ma = s_adx & (kama < kprev) & below

    trend = _pivot_trend(bars_df, int(p["pp_period"]), float(p["atr_factor"]), int(p["atr_period"]))
    tprev = np.concatenate([[np.nan], trend[:-1]])
    bsig, ssig = (trend == 1) & (tprev == -1), (trend == -1) & (tprev == 1)

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    ini_l = ini_s = 0.0
    last_l = last_s = 0
    pos = 0
    for i in range(m):
        lc1 = bool(long_ma[i - 1]) if i else False
        sc1 = bool(short_ma[i - 1]) if i else False
        long_cond = lc1 and ini_l == -1
        short_cond = sc1 and ini_s == 1
        ini_l = 1.0 if lc1 else (-1.0 if sc1 else ini_l)
        ini_s = 1.0 if lc1 else (-1.0 if sc1 else ini_s)
        if long_cond:
            last_l = i + 1
        if short_cond:
            last_s = i + 1
        close_all = (ssig[i] and last_l > last_s) or (bsig[i] and last_s > last_l)
        if close_all and pos != 0:
            (lx if pos == 1 else sx)[i] = True
            pos = 0
        elif long_ma[i] and pos != 1:
            le[i], pos = True, 1
        elif short_ma[i] and pos != -1:
            se[i], pos = True, -1
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
