"""ADX MASANAKAMURA 22 > 19 direction with a range filter of the open, SAR 0.5 / 0.2 / 0.4, an open-EMA 12 / 16 oscillator over its SMA 9 and volume over 2.7 x its SMA 33 (or a close beyond a 20-bar 3-sd band of highs with volume over 3.3 x its SMA 20), 4-hour bars, entered through the script's own long / short state machine: the long set goes long, the short set goes short, with a 0.7 % (long) / 0.9 % (short) target and a 5 % stop measured from the script's anchor close; reversing.
Port of FMZ strategy #380294 "Bad guy strategy" (坏b的策略 (Bad guy strategy)).

FMZ source id: 380294

Source
    https://www.fmz.com/strategy/380294 (PineScript v4, FMZ last modified 2022-08-29 20:51:48).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 49-334), src open; ADX MASANAKAMURA 22 / 19; range filter 19 x 2.5; EMA 12 / 16, SMA 9; SAR 0.5 / 0.2 / 0.4; volume SMA 20 x 3.3 and SMA 33 x 2.7; BB high 20 x 3; TP 0.7 % / 0.9 %, SL 5 % of the anchor; window 2000 .. 3333
    longCond = (L_adx and g2 and L_d and L_f and L_a3) or (... and g1) or (L_adx and L_BB_2 and g1 and g2 and L_d and L_a3);  shortCond mirror (S_BB_2 = close > l1, as written)
    long = longCond and (not in_longCondition or Final_Long_tp or Final_Long_sl or a later tp / sl than the last long condition) -> entry L;  short mirror -> entry S
    exit("TP_L", "L", profit = last_open_long x 0.7 % / mintick, loss = last_open_long x 5 % / mintick);  exit("TP_S", "S", 0.9 %, 5 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's CondIni state machine runs as written (Position "Both" never equals "BOTH", so the
      stop test takes its second branch; last_long_sl reads the previous bar's Final_Long_sl, as written).
      A long condition is a long set on the previous bar when the last set was short or the script's own
      target / stop reset it; its previous close is the anchor last_open_longCondition. The exits are
      distances from the fill: 0.7 % / 0.9 % and 5 % of the anchor, as fractions of the fill with the
      anchor of the fill bar (the script re-sends them each bar, and the fill bar itself uses the previous
      bar's anchor there: mark trailing_stop_pending). The second long set is the first with one more
      volume test, as written. A bar with both sides takes the short (the later call). The leverage block
      is off and feeds nothing. The author's date window is dropped. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the script's anchor.
    2 generic: PASS, ADX / range filter / SAR / volume confluence with a re-arming state machine.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000, commission 0.04 % and a risk input stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 3.3 x sma(volume, 20) and volume > 2.7 x sma(volume, 33); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2000 .. 3333 window dropped).
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_380294_adx_mn22_range_filter_sar_volume_state_machine_anchor_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_l": [0.007, 0.012],
    "sl": [0.05, 0.03],
}
DEFAULT_PARAMS = {"tp_l": 0.007, "tp_s": 0.009, "sl": 0.05, "adx_len": 22, "th": 19.0, "c1": 19, "c2": 2.5,
                  "x1": 12, "x2": 16, "x3": 9, "u": 3.3, "o": 20, "y": 2.7, "i": 33, "v1": 0.5, "v2": 0.2,
                  "v3": 0.4, "h1": 20, "j": 3.0}


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


def _range_filter(src, per, mult):
    """The source's q(): smoothed range, ratcheting filter, up / down run counts (nz as written)."""
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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's sar as documented (pine_sar)."""
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


def _conds(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    th = float(p["th"])
    dip, dim, adx = _adx_masanakamura(bars_df, int(p["adx_len"]))
    l_adx, s_adx = (dip > dim) & (adx > th), (dip < dim) & (adx > th)
    a3 = o.ewm(span=int(p["x1"]), adjust=False).mean() - o.ewm(span=int(p["x2"]), adjust=False).mean()
    a4 = a3.rolling(int(p["x3"])).mean()
    l_a3, s_a3 = a3 > a4, a3 < a4
    d7, d8, d9, d10 = _range_filter(o, int(p["c1"]), float(p["c2"]))
    l_d = pd.Series((h.to_numpy() > d8 + d7) & (d9 > 0), index=c.index)
    s_d = pd.Series((lo.to_numpy() < d8 - d7) & (d10 > 0), index=c.index)
    f = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                       float(p["v1"]), float(p["v2"]), float(p["v3"])), index=c.index)
    l_f, s_f = f < c, f > c
    g1 = v > v.rolling(int(p["o"])).mean() * float(p["u"])
    g2 = v > v.rolling(int(p["i"])).mean() * float(p["y"])
    n = int(p["h1"])
    k, sd = h.rolling(n).mean(), h.rolling(n).std(ddof=0) * float(p["j"])
    l_bb, s_bb = c > k + sd, c > k - sd                    # S_BB_2 = close > l1, as written
    l1 = l_adx & g2 & l_d & l_f & l_a3
    s1 = s_adx & g2 & s_d & s_f & s_a3
    l2, s2 = l1 & g1, s1 & g1
    l3 = l_adx & l_bb & g1 & g2 & l_d & l_a3
    s3 = s_adx & s_bb & g1 & g2 & s_d & s_a3
    return (l1 | l2 | l3).to_numpy(), (s1 | s2 | s3).to_numpy()


def _machine(bars_df, p):
    """The source's CondIni state machine: entry signals and the anchor closes of each bar."""
    lc, sc = _conds(bars_df, p)
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    tp_l, tp_s, sl = float(p["tp_l"]), float(p["tp_s"]), float(p["sl"])
    m = len(c)
    long_, short_ = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lol_a, los_a = np.zeros(m), np.zeros(m)
    ci_l = ci_s = ci_lsl = ci_ssl = 0
    lc_p = sc_p = False
    lol = los = 0.0
    last_l = last_s = 0
    l_tp_t = s_tp_t = l_sl_t = s_sl_t = 0
    f_l_sl_v = f_s_sl_v = False
    for i in range(m):
        t = i + 1
        ci_l_p, ci_s_p = ci_l, ci_s
        ci_l = 1 if lc_p else (-1 if sc_p else ci_l_p)
        ci_s = 1 if lc_p else (-1 if sc_p else ci_s_p)
        long_c = lc_p and ci_l_p == -1
        short_c = sc_p and ci_s_p == 1
        if long_c:
            lol, last_l = c[i - 1], t
        if short_c:
            los, last_s = c[i - 1], t
        in_l, in_s = last_l > last_s, last_s > last_l
        long_tp = h[i] > lol * (1 + tp_l) and in_l
        short_tp = lo[i] < los * (1 - tp_s) and in_s
        l_tp_p, s_tp_p, l_sl_p, s_sl_p = l_tp_t, s_tp_t, l_sl_t, s_sl_t
        if long_tp:
            l_tp_t = t
        if short_tp:
            s_tp_t = t
        f_l_tp = long_tp and last_l > l_tp_p and last_l > l_sl_p
        f_s_tp = short_tp and last_s > s_tp_p and last_s > s_sl_p
        long_sl = lo[i] <= (1 - sl) * lol and not (o[i] < (1 - sl) * lol)
        short_sl = h[i] >= (1 + sl) * los and not (o[i] > (1 + sl) * los)
        f_l_sl0 = long_sl and ci_lsl == -1 and not f_l_tp       # Position "Both" != "BOTH": second branch
        f_s_sl0 = short_sl and ci_ssl == -1 and not f_s_tp
        if f_l_sl_v:                                            # last_long_sl reads the previous Final_Long_sl
            l_sl_t = t
        if f_s_sl_v:
            s_sl_t = t
        f_l_sl = f_l_sl0 and last_l > l_tp_p and last_l > l_sl_p
        f_s_sl = f_s_sl0 and last_s > s_tp_p and last_s > s_sl_p
        ci_lsl = 1 if (f_l_tp or f_l_sl or short_c) else (-1 if long_c else ci_lsl)
        ci_ssl = 1 if (f_s_tp or f_s_sl or long_c) else (-1 if short_c else ci_ssl)
        a, b = bool(lc[i]), bool(sc[i])
        long_[i] = a and ((not in_l) or f_l_tp or f_l_sl or (not long_c and l_tp_t > last_l)
                          or (not long_c and l_sl_t > last_l))
        short_[i] = b and ((not in_s) or f_s_tp or f_s_sl or (not short_c and s_tp_t > last_s)
                           or (not short_c and s_sl_t > last_s))
        if f_l_tp or f_l_sl:
            ci_l = -1
        if f_s_tp or f_s_sl:
            ci_s = 1
        f_l_sl_v, f_s_sl_v = f_l_sl, f_s_sl
        lol_a[i], los_a[i] = lol, los
        lc_p, sc_p = a, b
    ix = bars_df.index
    return pd.Series(long_, index=ix), pd.Series(short_, index=ix), pd.Series(lol_a, index=ix), pd.Series(los_a, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _machine(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lol, los = _machine(bars_df, p)
    o = bars_df["open"]
    sf = se.shift(1, fill_value=False)               # a short fills on this bar: the short anchor
    anchor = los.where(sf, lol)                       # the fill bar's anchor (known at its open)
    sl_f = float(p["sl"]) * anchor / o
    tp_f = pd.Series(np.where(sf, float(p["tp_s"]), float(p["tp_l"])), index=o.index) * anchor / o
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
