"""A confluence of ADX (MASANAKAMURA 19 > 16), a range filter of hl2, a close-vs-31-bars-back test, MACD 13 / 19 / 19 of hl2, the VWMA 61 slope, volume over 1.1 x its EMA 61, RSI 50 bands and a 58-bar money-flow line (or a Stochastic 12 / 72 band-crossing scalp), 30-minute bars: the long set goes long, the short set goes short; only shorts carry the 1.9 % / 8.1 % bracket (the two exits share one id); reversing.
Port of FMZ strategy #376259 "EtHEriOOOm 30MIN" (EtHEriOOOm [30MIN]).

FMZ source id: 376259

Source
    https://www.fmz.com/strategy/376259 (PineScript, no @version line, FMZ last modified 2022-08-02 23:44:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 68-432), src hl2; ADX MASANAKAMURA 19 / 16; range filter 35 x 0.2; JMA 31 (close[1]); MACD 13 / 19 / 19 (SMA signal); VWMA 61; volume EMA 61 x 1.1; RSI 50; MFI 58 x 3; stoch 12 / 72 with 67 / 42; TP 1.9 %, SL 8.1 % of the close in ticks; window 2019-06 .. 2222
    L_second = (L_adx and L_RF and L_jma and L_macd and L_s_ma and volumegood and L_rsi and L_mfi) or crossover(67, k) -> entry L;  mirror with crossunder(42, k) -> entry S
    exit("S_tp/sl", "L", profit = close x 0.019 / mintick, loss = close x 0.081 / mintick);  exit("S_tp/sl", "S", same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar size is the one the title states (30MIN; no backtest header). Both exits use the id
      "S_tp/sl", so the second (for "S") replaces the first every bar: only shorts have the bracket and longs
      end at a short entry (a weird case, as #363970). The bracket distances are 1.9 % / 8.1 % of the latest
      close from the entry; the port fixes them at the signal close as fractions of the fill (mark
      trailing_stop_pending). The JMA line is close[1] (repainting off), so its test is close[1] against the
      mean of close[1] and close[32]. The money-flow helper returns its last line whatever the zero tests
      say (Pine returns the last expression). The range filter, ADX and VWMA are the source's (as #363970 /
      #365126). The author's date window is dropped (the C118-C124 reading). A bar with both sets takes the
      short. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size,
      capital and commission are sizing / costs, not ported.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only bracket as fractions of the fill.
    2 generic: PASS, multi-indicator trend confluence with a stochastic scalp.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: 100 % of equity, capital 10000 and commission 0.04 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 1.1 x ema(volume, 61), the VWMA 61 slope and the 58-bar money-flow line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2019 .. 2222 window dropped).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_376259_adx_range_filter_vwma_volume_mfi_stoch_scalp_confluence_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # the title's "30MIN" (no backtest header)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rvol_trigger": [1.1, 1.5],
    "th": [16.0, 25.0],
}
DEFAULT_PARAMS = {"rvol_trigger": 1.1, "th": 16.0, "adx_len": 19, "per": 35, "mult": 0.2, "jma_len": 31,
                  "fast": 13, "slow": 19, "signal": 19, "ma_len": 61, "vol_len": 61, "len_3": 50,
                  "mfi_len": 58, "lengthd": 12, "smooth_k": 72, "ul": 67, "ll": 42, "tp": 0.019, "sl": 0.081}


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
    """The source's rsi_3: down == 0 -> 100, up == 0 -> 0, else 100 - 100 / (1 + up / down)."""
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _nz(v):
    return 0.0 if np.isnan(v) else v


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


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    src = (h + lo) / 2
    th = float(p["th"])
    dip, dim, adx = _adx_masanakamura(bars_df, int(p["adx_len"]))
    l_adx, s_adx = (dip > dim) & (adx > th), (dip < dim) & (adx > th)
    smr, filt, up, dn = _range_filter(src, int(p["per"]), float(p["mult"]))
    l_rf = pd.Series((h.to_numpy() > filt + smr) & (up > 0), index=c.index)
    s_rf = pd.Series((lo.to_numpy() < filt - smr) & (dn > 0), index=c.index)
    s0 = c.shift(1)
    jsa = (s0 + s0.shift(int(p["jma_len"]))) / 2
    l_jma, s_jma = s0 > jsa, s0 < jsa
    macd = src.ewm(span=int(p["fast"]), adjust=False).mean() - src.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    nv = int(p["ma_len"])
    vw = (src * v).rolling(nv).sum() / v.rolling(nv).sum()
    speed = (vw / vw.shift(1) - 1) * 100
    vol_ok = v > float(p["rvol_trigger"]) * v.ewm(span=int(p["vol_len"]), adjust=False).mean()
    r3 = _rsi_custom(c, int(p["len_3"]))
    hlc3 = (h + lo + c) / 3
    ch = hlc3.diff()
    mn = int(p["mfi_len"])
    mu = (v * hlc3.where(~(ch <= 0), 0.0)).rolling(mn).sum()
    ml = (v * hlc3.where(~(ch >= 0), 0.0)).rolling(mn).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        mf = 100.0 - 100.0 / (1.0 + mu / ml)               # the helper's last line, as written
    mfi = (mf - 50) * 3
    nd = int(p["lengthd"])
    ll_, hh_ = lo.rolling(nd).min(), h.rolling(nd).max()
    k = (100 * (c - ll_) / (hh_ - ll_).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    ul, lw = float(p["ul"]), float(p["ll"])
    l_scalp = (k < ul) & (k.shift(1) >= ul)                 # crossover(67, k)
    s_scalp = (k > lw) & (k.shift(1) <= lw)                 # crossunder(42, k)
    l_basic = l_adx & l_rf & l_jma & (macd > sig) & (speed > 0) & vol_ok & (r3 < 70) & (mfi > 1)
    s_basic = s_adx & s_rf & s_jma & (macd < sig) & (speed < 0) & vol_ok & (r3 > 30) & (mfi < -1)
    return (l_basic | l_scalp), (s_basic | s_scalp)


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
