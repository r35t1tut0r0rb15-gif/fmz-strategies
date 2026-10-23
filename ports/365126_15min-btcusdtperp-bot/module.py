"""A twelve-filter confluence (ADX MASANAKAMURA 11 > 12, relative volume over 1.5 x its SMA 100, Parabolic SAR, RSI 70 band, MACD 25 / 50, cumulative volume delta over its SMA 45, SMA 5 / 30, VWMA 51 slope, a TWAP-style SMA 10, a 4-bar close test, a variance-adaptive filter and a 45-bar open-count momentum), 45-minute bars: all bullish starts a long, all bearish a short, re-armed by the script's own 0.8 % / 3.6 % hit tests; each trade has a 0.8 % target and 3.6 % stop from the entry; reversing.
Port of FMZ strategy #365126 "15MIN BTCUSDTPERP BOT" (15MIN BTCUSDTPERP BOT).

FMZ source id: 365126

Source
    https://www.fmz.com/strategy/365126 (PineScript v4, FMZ last modified 2022-06-20 10:25:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 114-461), src ohlc4; ADX MASANAKAMURA 11 / 12; range filter 13 x 1; SAR 0 / 0.006 / 1; RSI 70; TWAP 10; JMA 4 (close[1]); MACD 25 / 50 / 9 (SMA signal); delta 45; volume SMA 100 x 1.5; VWMA 51; momentum 45 / 12 / 9; TP 0.8 %, SL 3.6 % of the avg price
    Long = (DI+ > DI- and ADX > 12) and volume > 1.5 sma(volume, 100) and sar < close and rsi < 70 and macd > signal and cvd > sma(cvd, 45) and sma5 > sma30 and vwma(src, 51) rising and src > sma(src, 10) and close[1] > (close[1] + close[5]) / 2 and cts > cma and Main > Signal;  Short mirror
    long_last = Long and long_short[1] in (0, -1) -> entry L;  short_last mirror -> entry S;  long_short resets to 0 on the script's own 3.6 % / 0.8 % hit tests from the signal close;  the Short set has no TWAP term
    exit(qty_percent 100, profit = 0.8 % of the avg price, loss = 3.6 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The TWAP timeframe "0" is the chart's own, so the TWAP is the source price itself (weight 0 every
      bar) and its SMA 10 the line, as written; the JMA source is close[1] on historical bars (repainting
      off). The range filter is the source's variance-adaptive pair (cts vs cma, nz(..., src) seeds). The
      volume delta splits each bar's volume by the source's bull / bear power formulas; a bar where both
      are 0 adds nothing to the cumulative sum. The ADX is the MASANAKAMURA menu default (Wilder sums, SMA
      of DX); the SAR starts at 0 as written. long_short is the script's own state: it re-arms entries
      after its hit tests (the high / low against the signal close +/- the percents, from the bar after
      the signal) or the opposite signal. The bracket is a scalar fraction of the fill (as #440797).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size and the
      backtest-days input are sizing / unused. The source carries the Mozilla Public License 2.0 notice.
      FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, multi-indicator trend confluence with a self-re-arming state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the relative-volume filter, the cumulative volume delta and the VWMA 51 slope; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365126_twelve_filter_confluence_cvd_vwma_state_pct_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rvol_trigger": [1.5, 1.0],
    "th": [12.0, 20.0],
}
DEFAULT_PARAMS = {"rvol_trigger": 1.5, "th": 12.0, "adx_len": 11, "length0": 13, "mult": 1.0,
                  "sar_start": 0.0, "sar_inc": 0.006, "sar_max": 1.0, "len_3": 70, "smoothing": 10,
                  "jma_len": 4, "fast": 25, "slow": 50, "signal": 9, "period_ma": 45, "ma_length": 100,
                  "vwma_len": 51, "tmo_length": 45, "calc_length": 12, "smooth_length": 9,
                  "tp": 0.008, "sl": 0.036}


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


def _powers(o, h, lo, c):
    """The source's bullPower / bearPower nested iff chains."""
    c1 = c.shift(1)
    w = np.where
    up_bar, dn_bar = c > o, c < o
    bull = w(dn_bar, w(c1 < o, np.maximum(h - c1, c - lo), np.maximum(h - o, c - lo)),
             w(up_bar, w(c1 > o, h - lo, np.maximum(o - c1, h - lo)),
               w(h - c > c - lo, w(c1 < o, np.maximum(h - c1, c - lo), h - o),
                 w(h - c < c - lo, w(c1 > o, h - lo, np.maximum(o - c1, h - lo)),
                   w(c1 > o, np.maximum(h - o, c - lo), w(c1 < o, np.maximum(o - c1, h - lo), h - lo))))))
    bear = w(dn_bar, w(c1 > o, np.maximum(c1 - o, h - lo), h - lo),
             w(up_bar, w(c1 > o, np.maximum(c1 - lo, h - c), np.maximum(o - lo, h - c)),
               w(h - c > c - lo, w(c1 > o, np.maximum(c1 - o, h - lo), h - lo),
                 w(h - c < c - lo, w(c1 > o, np.maximum(c1 - lo, h - c), o - lo),
                   w(c1 > o, np.maximum(c1 - o, h - lo), w(c1 < o, np.maximum(o - lo, h - c), h - lo))))))
    return pd.Series(bull, index=c.index), pd.Series(bear, index=c.index)


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    src = (o + h + lo + c) / 4
    th = float(p["th"])
    dip, dim, adx = _adx_masanakamura(bars_df, int(p["adx_len"]))
    n0 = int(p["length0"])
    var = (src.rolling(n0).var(ddof=0) * float(p["mult"])).to_numpy(dtype=float)
    sma0 = src.rolling(n0).mean().to_numpy(dtype=float)
    sv = src.to_numpy(dtype=float)
    m = len(sv)
    cma, cts = np.full(m, np.nan), np.full(m, np.nan)
    cma_p = cts_p = np.nan
    for i in range(m):
        d1 = sma0[i] - cma_p
        d2 = sv[i] - cts_p
        secma = (0.0 if np.isnan(d1) else d1) ** 2
        sects = (0.0 if np.isnan(d2) else d2) ** 2
        ka = 1 - var[i] / secma if var[i] < secma else 0.0
        kb = 1 - var[i] / sects if var[i] < sects else 0.0
        cma[i] = ka * sma0[i] + (1 - ka) * (sv[i] if np.isnan(cma_p) else cma_p)
        cts[i] = kb * sv[i] + (1 - kb) * (sv[i] if np.isnan(cts_p) else cts_p)
        cma_p, cts_p = cma[i], cts[i]
    psar = _sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    sar_up = pd.Series(psar < c.to_numpy(dtype=float), index=c.index)
    d = c.diff()
    up3, dn3 = _rma(d.clip(lower=0), int(p["len_3"])), _rma((-d).clip(lower=0), int(p["len_3"]))
    rsi3 = (100 - 100 / (1 + up3 / dn3)).where(up3 != 0, 0.0).where(dn3 != 0, 100.0).where(up3.notna() & dn3.notna())
    bullish = src > src.rolling(int(p["smoothing"])).mean()
    s0 = c.shift(1)
    jsa = (s0 + s0.shift(int(p["jma_len"]))) / 2
    macd = src.ewm(span=int(p["fast"]), adjust=False).mean() - src.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    bp, sp = _powers(o, h, lo, c)
    tot = bp + sp
    delta = ((bp - sp) / tot.where(tot != 0) * v).fillna(0.0)
    cvd = delta.cumsum()
    cvd_ma = cvd.rolling(int(p["period_ma"])).mean()
    vma = v.rolling(int(p["ma_length"])).mean()
    vol_ok = v > float(p["rvol_trigger"]) * vma
    ma5, ma30 = c.rolling(5).mean(), c.rolling(30).mean()
    nv = int(p["vwma_len"])
    vw = (src * v).rolling(nv).sum() / v.rolling(nv).sum()
    speed = (vw / vw.shift(1) - 1) * 100
    data = pd.Series(0.0, index=c.index)
    for i in range(1, int(p["tmo_length"])):
        oi = o.shift(i)
        data = data + (c > oi).astype(float) - (c < oi).astype(float)
    e5 = data.ewm(span=int(p["calc_length"]), adjust=False).mean()
    main = e5.ewm(span=int(p["smooth_length"]), adjust=False).mean()
    msig = main.ewm(span=int(p["smooth_length"]), adjust=False).mean()
    cts_s, cma_s = pd.Series(cts, index=c.index), pd.Series(cma, index=c.index)
    long_c = ((dip > dim) & (adx > th) & vol_ok & sar_up & (rsi3 < 70) & (macd > sig) & (cvd > cvd_ma)
              & (ma5 > ma30) & (speed > 0) & bullish & (s0 > jsa) & (cts_s > cma_s) & (main > msig))
    short_c = ((dip < dim) & (adx > th) & vol_ok & ~sar_up & (rsi3 > 30) & (macd < sig) & (cvd < cvd_ma)
               & (ma5 < ma30) & (speed < 0) & (s0 < jsa) & (cts_s < cma_s) & (main < msig))   # no TWAP term, as written
    lc, sc = long_c.to_numpy(), short_c.to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp"]), float(p["sl"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ls, lp, sp_, lb, sb = 0, np.nan, np.nan, -1, -1
    for i in range(m):
        prev = ls
        long_last = lc[i] and prev in (0, -1)
        short_last = sc[i] and prev in (0, 1)
        ls = 1 if long_last else (-1 if short_last else prev)
        if long_last:
            lp, lb = cv[i], i
        if short_last:
            sp_, sb = cv[i], i
        l_ok = lb >= 0 and i - lb >= 1
        s_ok = sb >= 0 and i - sb >= 1
        l_hit = ls == 1 and l_ok and (lv[i] < lp * (1 - sl) or hv[i] > lp * (1 + tp))
        s_hit = ls == -1 and s_ok and (hv[i] > sp_ * (1 + sl) or lv[i] < sp_ * (1 - tp))
        if ls in (1, 0) and l_ok and l_hit:
            ls = 0
        elif ls in (-1, 0) and s_ok and s_hit:
            ls = 0
        le[i], se[i] = long_last, short_last
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(se, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se & ~le, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
