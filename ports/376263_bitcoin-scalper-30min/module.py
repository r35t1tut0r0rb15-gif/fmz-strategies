"""Three entry sets, 30-minute bars: an ADX 22 test (as written, DI+ under DI- for longs) with RSI 67 under 48 and an RMI 30 / 12 crossing over 33; or a 58-bar money-flow line with ADX MASANAKAMURA, a close over the last 3 / 1 pivot high, a rising MESA cloud of highs and volume over 2.6 x its SMA 21; or a Heikin-Ashi pullback-exit scalp with the ADX test: the long sets go long, the short sets go short; only shorts carry the 2 % / 8 % bracket (the two exits share one id); reversing.
Port of FMZ strategy #376263 "Bitcoin Scalper 30MIN" (Bitcoin Scalper [30MIN]).

FMZ source id: 376263

Source
    https://www.fmz.com/strategy/376263 (PineScript v4, FMZ last modified 2022-08-02 23:58:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 66-569), src high; RMI 30 / 12, 33 / 70; ADX 22 / 15 (CLASSIC and MASANAKAMURA); RSI 67, 48; pivots 3 / 1; cloud 23; volume SMA 21 x 2.6; scalping HA 4 / 10 / 120, lookback 3; TP 2 %, SL 8 % of the close in ticks; qty = volume leverage 1-2
    L_ = L_adx and L_rsi and L_rmi or L_mfi and L_adx_m and close > top and L_cloud and Volume or L_scalp and L_adx -> entry L (qty = Lev_vol);  S_ mirror -> entry S
    L_adx = DI+ < DI- and ADX > 15;  S_adx = DI+ < DI- and ADX < 15   (as written);  exit("S_tp/sl", "L", profit = close x 0.02 / mintick, loss = close x 0.08 / mintick);  exit("S_tp/sl", "S", same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar size is the one the title states (30MIN; no backtest header). The ADX tests are kept as
      written (both use DI+ < DI-; the short one needs ADX under the threshold). Both exits use the id
      "S_tp/sl", so the second (for "S") replaces the first: only shorts have the bracket (a weird case, as
      #363970); the distances are fixed at the signal close as fractions of the fill (mark
      trailing_stop_pending). The Heikin-Ashi series are the chart's own HA candles (seeded (open + close)
      / 2). The money-flow helper returns its last line (Pine returns the last expression). "and" binds
      before "or" in the three sets, as written. The pivot level is the latest 3 / 1 pivot high (low).
      The volume-based quantity (1 or 2 contracts) is sizing and is not ported. The author's date window is
      dropped. A bar with both sets takes the short. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). The source carries the Mozilla Public License 2.0 notice.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only bracket as fractions of the fill.
    2 generic: PASS, RMI / money-flow / Heikin-Ashi scalp entry sets.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: qty = min(2, max(1, round(volume / sma(volume, 70)))) and 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the 58-bar money-flow line and volume > 2.6 x sma(volume, 21) (and the not-ported quantity); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 1997 .. 3333 window dropped).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_376263_rmi_mfi_pivot_cloud_ha_scalp_sets_short_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # the title's "30MIN" (no backtest header)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "volume_f": [2.6, 1.5],
    "rmi_len": [30, 14],
}
DEFAULT_PARAMS = {"volume_f": 2.6, "rmi_len": 30, "rmi_mom": 12, "rmi_os": 33, "rmi_ob": 70, "adx_len": 22,
                  "th": 15.0, "rsi_len": 67, "rsi_os": 48, "left": 3, "right": 1, "cloud_len": 23, "vol_len": 21,
                  "hilo_len": 4, "fast_ema": 10, "medium_ema": 120, "lookback": 3, "mfi_len": 58,
                  "tp": 0.02, "sl": 0.08}


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


def _rsi_custom(x, n):
    """The source's RSI(): down == 0 -> 100, up == 0 -> 0, else 100 - 100 / (1 + up / down)."""
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


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


def _barssince(cond):
    """Pine barssince: bars since cond was last true (NaN before the first true)."""
    a = np.asarray(cond, dtype=bool)
    idx = np.maximum.accumulate(np.where(a, np.arange(len(a)), -1))
    return np.where(idx >= 0, np.arange(len(a)) - idx, np.nan)


def _ha_scalp(b, hilo, fast, medium, lookback):
    """The source's Heikin-Ashi pullback-exit scalp: TradeDirection state, entries when it leaves 0."""
    o, h, lo, c = (b[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    ha_c = (o + h + lo + c) / 4
    ha_o = np.full(m, np.nan)
    for i in range(m):
        ha_o[i] = (o[i] + c[i]) / 2 if i == 0 else (ha_o[i - 1] + ha_c[i - 1]) / 2
    ha_h, ha_l = np.maximum(h, np.maximum(ha_o, ha_c)), np.minimum(lo, np.minimum(ha_o, ha_c))
    ix = b.index
    hc, hl_, hh_ = pd.Series(ha_c, index=ix), pd.Series(ha_l, index=ix), pd.Series(ha_h, index=ix)
    fe, me = hc.ewm(span=fast, adjust=False).mean(), hc.ewm(span=medium, adjust=False).mean()
    pac_c = hc.ewm(span=hilo, adjust=False).mean().to_numpy()
    pac_l = hl_.ewm(span=hilo, adjust=False).mean().to_numpy()
    pac_u = hh_.ewm(span=hilo, adjust=False).mean().to_numpy()
    fe, me = fe.to_numpy(), me.to_numpy()
    trend = np.where((fe > me) & (pac_l > me), 1, np.where((fe < me) & (pac_u < me), -1, 0))
    bs_b, bs_a = _barssince(ha_c < pac_c), _barssince(ha_c > pac_c)
    exit_u = (ha_o < pac_u) & (ha_c > pac_u) & (bs_b <= lookback)
    exit_l = (ha_o > pac_l) & (ha_c < pac_l) & (bs_a <= lookback)
    buy, sell = (trend == 1) & exit_u, (trend == -1) & exit_l
    lsc, ssc = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    td = 0
    for i in range(m):
        prev = td
        if td == 1 and ha_c[i] < pac_c[i]:
            td = 0
        elif td == -1 and ha_c[i] > pac_c[i]:
            td = 0
        elif td == 0 and buy[i]:
            td = 1
        elif td == 0 and sell[i]:
            td = -1
        lsc[i], ssc[i] = prev == 0 and td == 1, prev == 0 and td == -1
    return pd.Series(lsc, index=ix), pd.Series(ssc, index=ix)


def _pivot_level(x, side, left, right):
    """valuewhen(pivothigh / pivotlow(x, left, right), x[right], 0): the latest strict pivot value."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    hit = ((centre > lft) & (centre > rgt)).to_numpy()
    vals = x.shift(right).to_numpy(dtype=float)
    idx = np.maximum.accumulate(np.where(hit, np.arange(len(hit)), -1))
    return pd.Series(np.where(idx >= 0, vals[np.maximum(idx, 0)], np.nan), index=x.index)


def _rmi(c, n, m):
    up = (c - c.shift(m)).clip(lower=0).ewm(span=n, adjust=False).mean()
    dn = (c.shift(m) - c).clip(lower=0).ewm(span=n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 0.0).where(dn.notna())


def _signals(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    th = float(p["th"])
    plus, minus, adx = _dmi(bars_df, int(p["adx_len"]))
    l_adx = (plus < minus) & (adx > th)                   # as written
    s_adx = (plus < minus) & (adx < th)                   # as written
    pm, mm_, am = _adx_masanakamura(bars_df, int(p["adx_len"]))
    l_adx_m, s_adx_m = (pm > mm_) & (am > th), (pm < mm_) & (am > th)
    r = _rsi_custom(c, int(p["rsi_len"]))
    l_rsi, s_rsi = r < float(p["rsi_os"]), r > float(p["rsi_os"])
    rmi = _rmi(c, int(p["rmi_len"]), int(p["rmi_mom"]))
    os_, ob_ = float(p["rmi_os"]), float(p["rmi_ob"])
    l_rmi = (rmi > os_) & (rmi.shift(1) <= os_)
    s_rmi = (rmi < ob_) & (rmi.shift(1) >= ob_)
    hlc3 = (h + lo + c) / 3
    ch = hlc3.diff()
    mn = int(p["mfi_len"])
    mu = (v * hlc3.where(~(ch <= 0), 0.0)).rolling(mn).sum()
    ml = (v * hlc3.where(~(ch >= 0), 0.0)).rolling(mn).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        mfi = (100.0 - 100.0 / (1.0 + mu / ml) - 50) * 3       # the helper's last line, as written
    top = _pivot_level(h, 1, int(p["left"]), int(p["right"]))
    bot = _pivot_level(lo, -1, int(p["left"]), int(p["right"]))
    n = int(p["cloud_len"])
    er = (h - h.shift(n)).abs() / h.diff().abs().rolling(n).sum()
    kama = _cloud(h, er)
    vol_ok = v > v.rolling(int(p["vol_len"])).mean() * float(p["volume_f"])
    lsc, ssc = _ha_scalp(bars_df, int(p["hilo_len"]), int(p["fast_ema"]), int(p["medium_ema"]), int(p["lookback"]))
    l_ = (l_adx & l_rsi & l_rmi) | ((mfi > 2) & l_adx_m & (c > top) & (kama > kama.shift(1)) & vol_ok) | (lsc & l_adx)
    s_ = (s_adx & s_rsi & s_rmi) | ((mfi < -2) & s_adx_m & (c < bot) & (kama < kama.shift(1)) & vol_ok) | (ssc & s_adx)
    return l_, s_


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


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
