"""A confluence of ADX (MASANAKAMURA 13 > 15), a MESA cloud of highs, Parabolic SAR, a range filter of highs, MACD 6 / 8 / 17, a volume-weighted RSI 25 over 52, the EMA 66 slope and volume over 0.8 x its SMA 37 (or Bollinger / pivot-reversal shortcuts), 4-hour bars: the long side's state goes long, the short side's goes short; only shorts carry the 1.5 % / 7.2 % bracket (the two exits share one id); reversing.
Port of FMZ strategy #363970 "Johnys BOT" (Johny's BOT [60MIN]).

FMZ source id: 363970

Source
    https://www.fmz.com/strategy/363970 (PineScript v4, FMZ last modified 2022-05-18 10:24:18).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 114-590), src high; ADX MASANAKAMURA 13 / 15; cloud 7; SAR 0.015 / 0.018 / 0.1; range filter 10 x 1.5; MACD 6 / 8 / 17 (SMA signal); volume x 0.8 over SMA 37; RSI-volume 25 > 52; BB 10 x 2.1 of high; EMA 66 speed; pivots 15 / 7 with RSI 14 64 / 34; TP 1.5 %, SL 7.2 % of the close in ticks
    L_third = (L_adx and L_cloud and L_sar and L_RF and L_macd and L_rsi and L_s_ma and Volume) or (L_BB and L_adx and L_sar and L_rsi) or (L_REV and L_adx and L_sar and Volume) -> entry L;  mirror -> entry S
    exit("S_tp/sl", "L", profit = close x 0.015 / mintick, loss = close x 0.072 / mintick);  exit("S_tp/sl", "S", same)   (both every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both strategy.exit calls use the id "S_tp/sl", so the second (for "S") replaces the first on every
      bar: as written only shorts have the take-profit / stop and longs end at a short entry (a weird case,
      reported). The bracket distances are 1.5 % / 7.2 % of the latest close from the entry price; the port
      fixes them at the signal close as fractions of the fill (re-sent with each close afterwards: mark
      trailing_stop_pending). "and" binds before "or" in the three condition sets, as written. The ADX is
      the source's MASANAKAMURA menu default (Wilder sums, SMA of DX); the cloud is the MESA KAMA of
      #360018 on highs (length 7); the range filter is the source's (EMA of |change|, smoothed x 1.5, a
      ratcheting filter with up / down counts); RSI_V is a WiMA-smoothed RSI of volume-weighted high
      changes; the pivot reversal uses pivots 15 / 7 crossed by one tick (read at the 0.1 tick of 42000,
      2.381e-06 of the level) with RSI 14 limits. A bar with both states takes the short (the later
      call). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1
      hour: mark coarse_bar_stop. The 100 % of equity size, capital and commission are sizing / costs, not
      ported. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only bracket as fractions of the fill.
    2 generic: PASS, multi-indicator trend confluence with shortcuts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000 and commission 0.04 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in RSI_V (volume-weighted high changes) and volume > sma(volume, 37) x 0.8; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_363970_adx_cloud_sar_range_filter_macd_volume_rsi_confluence_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "volume_f": [0.8, 1.2],
    "th": [15.0, 25.0],
}
DEFAULT_PARAMS = {"volume_f": 0.8, "th": 15.0, "adx_len": 13, "cloud_len": 7, "sar_start": 0.015,
                  "sar_inc": 0.018, "sar_max": 0.1, "rf_per": 10, "rf_mult": 1.5, "fast": 6, "slow": 8,
                  "signal": 17, "vol_len": 37, "rsi_len": 25, "bb_per": 10, "bb_dev": 2.1, "ma_len": 66,
                  "left_bars": 15, "right_bars": 7, "rsi_ob": 64, "rsi_os": 34, "tp": 0.015, "sl": 0.072,
                  "tick_frac": 2.380952e-06}


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


def _adx_masanakamura(b, n):
    """The source's calcADX_Masanakamura: Wilder running sums with nz(), DX averaged by an SMA."""
    h, lo, c = (b[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    dip, dim = np.full(m, np.nan), np.full(m, np.nan)
    s_tr = s_p = s_m = 0.0
    for i in range(m):
        c1 = c[i - 1] if i else 0.0
        h1 = h[i - 1] if i else 0.0
        l1 = lo[i - 1] if i else 0.0
        tr = max(h[i] - lo[i], abs(h[i] - c1), abs(lo[i] - c1))
        dmp = max(h[i] - h1, 0.0) if h[i] - h1 > l1 - lo[i] else 0.0
        dmm = max(l1 - lo[i], 0.0) if l1 - lo[i] > h[i] - h1 else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        if s_tr != 0:
            dip[i], dim[i] = s_p / s_tr * 100, s_m / s_tr * 100
    dip_s, dim_s = pd.Series(dip, index=b.index), pd.Series(dim, index=b.index)
    dx = (dip_s - dim_s).abs() / (dip_s + dim_s) * 100
    return dip_s, dim_s, dx.rolling(n).mean()


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


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


def _range_filter(src, per, mult):
    """The source's Range_filter: smoothed range, ratcheting filter, up / down run counts (nz as written)."""
    avrng = (src - src.shift(1)).abs().ewm(span=per, adjust=False).mean()
    smr = (avrng.ewm(span=per * 2 - 1, adjust=False).mean() * mult).to_numpy(dtype=float)
    s = src.to_numpy(dtype=float)
    m = len(s)
    filt, up, dn = np.full(m, np.nan), np.zeros(m), np.zeros(m)
    fp, up_p, dn_p = np.nan, 0.0, 0.0
    for i in range(m):
        prev = _nz(fp)
        if s[i] > prev:
            f = prev if (s[i] - smr[i]) < prev else s[i] - smr[i]
        else:
            f = prev if (s[i] + smr[i]) > prev else s[i] + smr[i]
        u = up_p + 1 if f > fp else (0.0 if f < fp else up_p)
        d = dn_p + 1 if f < fp else (0.0 if f > fp else dn_p)
        filt[i], up[i], dn[i] = f, u, d
        fp, up_p, dn_p = f, u, d
    return smr, filt, up, dn


def _pivot_value(x, side, left, right):
    """Pine pivothigh / pivotlow(left, right): the pivot's value at its confirmation bar, else NaN (strict)."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return x.shift(right).where((centre > lft) & (centre > rgt))


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    src = h
    th = float(p["th"])
    dip, dim, adx = _adx_masanakamura(bars_df, int(p["adx_len"]))
    l_adx, s_adx = (dip > dim) & (adx > th), (dip < dim) & (adx > th)
    n = int(p["cloud_len"])
    er = (src - src.shift(n)).abs() / src.diff().abs().rolling(n).sum()
    kama = _cloud(src, er)
    l_cloud, s_cloud = kama > kama.shift(1), kama < kama.shift(1)
    psar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                          float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"])), index=c.index)
    l_sar = psar < c
    s_sar = ~l_sar
    smr, filt, up, dn = _range_filter(src, int(p["rf_per"]), float(p["rf_mult"]))
    l_rf = pd.Series((h.to_numpy() > filt + smr) & (up > 0), index=c.index)
    s_rf = pd.Series((lo.to_numpy() < filt - smr) & (dn > 0), index=c.index)
    macd = src.ewm(span=int(p["fast"]), adjust=False).mean() - src.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    l_macd, s_macd = macd > sig, macd < sig
    ch = src.diff()
    upv = (ch.abs() * v).where(ch > 0, 0.0).to_numpy(dtype=float)
    dnv = (ch.abs() * v).where(ch < 0, 0.0).to_numpy(dtype=float)
    rl = int(p["rsi_len"])
    upt, dnt = np.zeros(len(upv)), np.zeros(len(dnv))
    a_p = b_p = 0.0
    for i in range(len(upv)):
        a_p = (upv[i] + a_p * (rl - 1)) / rl          # WiMA: var MA_s, nz(MA_s[1])
        b_p = (dnv[i] + b_p * (rl - 1)) / rl
        upt[i], dnt[i] = a_p, b_p
    with np.errstate(divide="ignore", invalid="ignore"):
        rsi_v = pd.Series(100 * upt / (upt + dnt), index=c.index)
    l_rsi, s_rsi = rsi_v > 52, rsi_v < 52
    vol_ok = v > v.rolling(int(p["vol_len"])).mean() * float(p["volume_f"])
    bp = int(p["bb_per"])
    ma1 = src.rolling(bp).mean()
    sd1 = src.rolling(bp).std(ddof=0) * float(p["bb_dev"])
    l_bb, s_bb = o > ma1 + sd1, o < ma1 - sd1
    av = src.ewm(span=int(p["ma_len"]), adjust=False).mean()
    speed = (av / av.shift(1) - 1) * 100
    l_sma, s_sma = speed > 0, speed < 0
    lb, rb = int(p["left_bars"]), int(p["right_bars"])
    swh, swl = _pivot_value(h, 1, lb, rb), _pivot_value(lo, -1, lb, rb)
    hprice = swh.where(swh.notna()).to_numpy(dtype=float)
    lprice = swl.where(swl.notna()).to_numpy(dtype=float)
    m = len(c)
    hp, lp = np.full(m, np.nan), np.full(m, np.nan)
    last_h = last_l = np.nan
    for i in range(m):
        if not np.isnan(hprice[i]):
            last_h = hprice[i]
        if not np.isnan(lprice[i]):
            last_l = lprice[i]
        hp[i], lp[i] = last_h, last_l
    tk = float(p["tick_frac"])
    hpu, lpd = pd.Series(hp * (1 + tk), index=c.index), pd.Series(lp * (1 - tk), index=c.index)
    x_up = ((h > hpu) & (h.shift(1) <= hpu.shift(1))).to_numpy()
    x_dn = ((lo < lpd) & (lo.shift(1) >= lpd.shift(1))).to_numpy()
    r14 = _rsi(c, 14).to_numpy(dtype=float)
    les, l_rev, s_rev = 0, np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(m):
        prev = les
        les = 1 if x_up[i] else (-1 if x_dn[i] else les)
        l_rev[i] = prev == -1 and les == 1 and r14[i] < float(p["rsi_ob"])
        s_rev[i] = (not l_rev[i]) and prev == 1 and les == -1 and r14[i] > float(p["rsi_os"])
    l_basic = l_adx & l_cloud & l_sar & l_rf & l_macd & l_rsi & l_sma & vol_ok
    s_basic = s_adx & s_cloud & s_sar & s_rf & s_macd & s_rsi & s_sma & vol_ok
    l_third = l_basic | (l_bb & l_adx & l_sar & l_rsi) | (pd.Series(l_rev, index=c.index) & l_adx & l_sar & vol_ok)
    s_third = s_basic | (s_bb & s_adx & s_sar & s_rsi) | (pd.Series(s_rev, index=c.index) & s_adx & s_sar & vol_ok)
    return l_third & ~s_third, s_third


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    o, c = bars_df["open"], bars_df["close"]
    sf = se.shift(1, fill_value=False)              # only the short has the shared-id exit
    sl_f = (float(p["sl"]) * c.shift(1) / o).where(sf)
    tp_f = (float(p["tp"]) * c.shift(1) / o).where(sf)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
