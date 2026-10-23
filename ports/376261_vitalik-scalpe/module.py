"""Four entry sets on the open as source: a close over the last 7 / 8 pivot high with ADX 22 > 13, SAR 0.7 / 0.2 / 0.38, a range filter, MACD 15 / 16 / 21 and RSI 50 of hlc3; a close over a 10-bar band of highs with volume over 1.8 x its SMA 33; an RMI 15 / 24 crossing over 31; or a Heikin-Ashi pullback-exit scalp with volume: the long sets go long, the short sets go short, each with a 0.9 % target and a 3.5 % stop, and everything is closed when a pivot-centre ATR trend turns against the script's own side; reversing.
Port of FMZ strategy #376261 "Vitalik Scalpe" (Vitalik Scalper).

FMZ source id: 376261

Source
    https://www.fmz.com/strategy/376261 (PineScript v4, FMZ last modified 2022-08-02 23:55:53).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 77-550), src open; ADX CLASSIC 22 / 13; pivots 7 / 8; volume SMA 33 x 1.8; SAR 0.7 / 0.2 / 0.38; range filter 15 x 1.6; MACD 15 / 16 / 21 (SMA signal); RSI 50 of hlc3; BB high 10 x 1; RMI 15 / 24, 31 / 63; scalping HA 6 / 10 / 120, lookback 7; ATR trend pp 2, factor 4, period 1; TP 0.9 %, SL 3.5 %; window 1997 .. 3333
    L_basic = L_1 or L_2 or L_3 or L_4 -> entry L;  S_basic mirror -> entry S (S_BB_2 = close > lb2, as written)
    exit("TP_L", "L", profit = last_open x 0.9 % / mintick, limit = nLongs >= 1 ? avg x 1.009, loss = last_open x 3.5 % / mintick);  mirror for S;  close_all(when = ssignal and in_longCondition or bsignal and in_shortCondition)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's own side (in_longCondition / in_shortCondition) is its CondIni state machine, run as
      written: a long condition is a long set on the previous bar after a short set (or after the script's
      own target / stop hit reset it), and its target / stop tests use that condition's previous close, not
      the real position. Since nLongs never exceeds 1 (a second long condition needs a reset or a short in
      between), the target is 0.9 % and the stop 3.5 %. The target (limit at the average price x 1.009, which
      has priority over profit) is a scalar fraction of the fill; the stop is 3.5 % of the signal close from
      the entry, fixed at the signal close as a fraction of the fill (the script re-sends it each bar from
      its own anchor: mark trailing_stop_pending). The close_all follows the entries in call order, so it only
      closes a position the bar's entries leave unchanged; a repeat entry on the close_all bar keeps the
      position (approximation). A bar with both sets takes the short (the later call). The Bollinger
      timeframe is the chart's. The Heikin-Ashi series are the chart's own HA candles. Pivots are strict.
      No backtest header or input names a bar size: FREQ = "bar_size_pending"; the bars come from the house
      bar_sizes.build_bars. The author's date window is dropped. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The source carries the Mozilla Public License 2.0 notice.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill; close-all on the trend flip.
    2 generic: PASS, four-set multi-indicator confluence with an ATR trend exit.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: 100 % of equity, capital 10000 and commission 0.03 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar by the house bar builder) in volume > 1.8 x sma(volume, 33) (sets 2 and 4); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 1997 .. 3333 window dropped).
REVERSAL INTENDED.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_376261_pivot_sar_range_filter_rmi_ha_scalp_sets_atr_trend_close_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "volume_f": [1.8, 1.5],
    "th": [13.0, 20.0],
}
DEFAULT_PARAMS = {"volume_f": 1.8, "th": 13.0, "adx_len": 22, "left": 7, "right": 8, "vol_len": 33,
                  "sar_start": 0.7, "sar_inc": 0.2, "sar_max": 0.38, "per": 15, "mult": 1.6, "fast": 15,
                  "slow": 16, "signal": 21, "len_3": 50, "bb_len": 10, "bb_dev": 1.0, "rmi_len": 15, "rmi_mom": 24,
                  "rmi_os": 31, "rmi_ob": 63, "hilo_len": 6, "fast_ema": 10, "medium_ema": 120, "lookback": 7,
                  "prd": 2, "factor": 4.0, "tp": 0.009, "sl": 0.035}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _pivot_level(x, side, left, right):
    """valuewhen(pivot, x[right], 0): the latest strict pivot value."""
    hit, vals = _pivot_hit(x, side, left, right)
    idx = np.maximum.accumulate(np.where(hit, np.arange(len(hit)), -1))
    return pd.Series(np.where(idx >= 0, vals[np.maximum(idx, 0)], np.nan), index=x.index)


def _rmi(c, n, m):
    up = (c - c.shift(m)).clip(lower=0).ewm(span=n, adjust=False).mean()
    dn = (c.shift(m) - c).clip(lower=0).ewm(span=n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 0.0).where(dn.notna())


def _atr_trend(b, prd, factor):
    """The source's pivot-centre ATR trend: returns the bsignal / ssignal flips."""
    h, lo, c = b["high"], b["low"], b["close"]
    ph_hit, ph_v = _pivot_hit(h, 1, prd, prd)
    pl_hit, pl_v = _pivot_hit(lo, -1, prd, prd)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    trend = np.ones(m)
    centre = tup_p = tdn_p = np.nan
    for i in range(m):
        ph = ph_v[i] if ph_hit[i] else np.nan
        pl = pl_v[i] if pl_hit[i] else np.nan
        lastpp = ph if (not np.isnan(ph) and ph != 0) else (pl if (not np.isnan(pl) and pl != 0) else np.nan)
        if not np.isnan(lastpp):
            centre = lastpp if np.isnan(centre) else (centre * 2 + lastpp) / 3
        up, dn = centre - factor * tr[i], centre + factor * tr[i]
        c1 = cv[i - 1] if i else np.nan
        tup = max(up, tup_p) if c1 > tup_p else up
        tdn = min(dn, tdn_p) if c1 < tdn_p else dn
        if cv[i] > tdn_p:
            trend[i] = 1
        elif cv[i] < tup_p:
            trend[i] = -1
        else:
            trend[i] = trend[i - 1] if i else 1
        tup_p, tdn_p = tup, tdn
    t1 = np.r_[np.nan, trend[:-1]]
    return (trend == 1) & (t1 == -1), (trend == -1) & (t1 == 1)


def _script_side(lc, sc, b, tp0, sl0):
    """The source's CondIni / in_longCondition state machine with its own target / stop resets."""
    h, lo, c = (b[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    in_l, in_s = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ci_l = ci_s = 0
    lc_p = sc_p = False
    lo_l = lo_s = 0.0
    last_l = last_s = 0
    n_l = n_s = np.nan
    sum_l = sum_s = 0.0
    pp_fix = np.nan
    l_tp = s_tp = l_sl = s_sl = 0
    for i in range(m):
        t = i + 1
        ci_l_p, ci_s_p = ci_l, ci_s
        ci_l = 1 if lc_p else (-1 if sc_p else ci_l_p)
        ci_s = 1 if lc_p else (-1 if sc_p else ci_s_p)
        long_c = lc_p and ci_l_p == -1
        short_c = sc_p and ci_s_p == 1
        if long_c:
            lo_l, last_l = c[i - 1], t
        if short_c:
            lo_s, last_s = c[i - 1], t
        il, is_ = last_l > last_s, last_s > last_l
        n_l, n_s = _nz(n_l), _nz(n_s)
        if long_c:
            n_l, n_s, sum_l, sum_s = n_l + 1, 0.0, lo_l + sum_l, 0.0
        if short_c:
            n_l, n_s, sum_s, sum_l = 0.0, n_s + 1, lo_s + sum_s, 0.0
        pp = np.nan
        if long_c:
            pp = sum_l / n_l if n_l != 0 else np.nan
        elif short_c:
            pp = sum_s / n_s if n_s != 0 else np.nan
        if not np.isnan(pp):
            pp_fix = pp
        tp_l = (tp0 / n_l if n_l > 1 else tp0)
        tp_s = (tp0 / n_s if n_s > 1 else tp0)
        long_tp = il and h[i] > pp_fix * (1 + tp_l)
        short_tp = is_ and lo[i] < pp_fix * (1 - tp_s)
        l_tp_p, s_tp_p, l_sl_p, s_sl_p = l_tp, s_tp, l_sl, s_sl
        if long_tp:
            l_tp = t
        if short_tp:
            s_tp = t
        f_l_tp = long_tp and last_l > l_tp_p and last_l > l_sl_p
        f_s_tp = short_tp and last_s > s_tp_p and last_s > s_sl_p
        sl = sl0 / max(1.0, n_l) if il else (sl0 / max(1.0, n_s) if is_ else sl0)
        n_lsl = il and lo[i] <= (1 - sl) * pp_fix
        n_ssl = is_ and h[i] >= (1 + sl) * pp_fix
        if n_lsl:
            l_sl = t
        if n_ssl:
            s_sl = t
        f_l_sl = n_lsl and last_l > l_sl_p and last_l > l_tp_p and not f_l_tp
        f_s_sl = n_ssl and last_s > s_sl_p and last_s > s_tp_p and not f_s_tp
        if f_l_tp or f_l_sl:
            ci_l, sum_l, n_l = -1, 0.0, np.nan
        if f_s_tp or f_s_sl:
            ci_s, sum_s, n_s = 1, 0.0, np.nan
        in_l[i], in_s[i] = il, is_
        lc_p, sc_p = bool(lc[i]), bool(sc[i])
    return in_l, in_s


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    src = o
    th = float(p["th"])
    plus, minus, adx = _dmi(bars_df, int(p["adx_len"]))
    l_adx, s_adx = (plus > minus) & (adx > th), (plus < minus) & (adx > th)
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"])), index=c.index)
    l_sar, s_sar = sar < c, sar > c
    top = _pivot_level(h, 1, int(p["left"]), int(p["right"]))
    bot = _pivot_level(lo, -1, int(p["left"]), int(p["right"]))
    vol_ok = v > v.rolling(int(p["vol_len"])).mean() * float(p["volume_f"])
    smr, filt, up, dn = _range_filter(src, int(p["per"]), float(p["mult"]))
    l_rf = pd.Series((h.to_numpy() > filt + smr) & (up > 0), index=c.index)
    s_rf = pd.Series((lo.to_numpy() < filt - smr) & (dn > 0), index=c.index)
    macd = src.ewm(span=int(p["fast"]), adjust=False).mean() - src.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    r3 = _rsi_custom((h + lo + c) / 3, int(p["len_3"]))
    l_rsi, s_rsi = r3 < 70, r3 > 30
    nb = int(p["bb_len"])
    ma2, sd2 = h.rolling(nb).mean(), h.rolling(nb).std(ddof=0) * float(p["bb_dev"])
    l_bb, s_bb = c > ma2 + sd2, c > ma2 - sd2           # S_BB_2 = close > lb2, as written
    rmi = _rmi(c, int(p["rmi_len"]), int(p["rmi_mom"]))
    os_, ob_ = float(p["rmi_os"]), float(p["rmi_ob"])
    l_rmi = (rmi > os_) & (rmi.shift(1) <= os_)
    s_rmi = (rmi < ob_) & (rmi.shift(1) >= ob_)
    lsc, ssc = _ha_scalp(bars_df, int(p["hilo_len"]), int(p["fast_ema"]), int(p["medium_ema"]), int(p["lookback"]))
    l_ = ((c > top) & l_adx & l_sar & l_rf & (macd > sig) & l_rsi) | (l_bb & l_rf & vol_ok & l_rsi) \
        | (l_rmi & l_adx & l_sar & l_rsi) | (lsc & l_adx & l_rf & vol_ok & l_rsi)
    s_ = ((c < bot) & s_adx & s_sar & s_rf & (macd < sig) & s_rsi) | (s_bb & s_rf & vol_ok & s_rsi) \
        | (s_rmi & s_adx & s_sar & s_rsi) | (ssc & s_adx & s_rf & vol_ok & s_rsi)
    bsig, ssig = _atr_trend(bars_df, int(p["prd"]), float(p["factor"]))
    in_l, in_s = _script_side(l_.to_numpy(), s_.to_numpy(), bars_df, float(p["tp"]), float(p["sl"]))
    close_all = pd.Series((ssig & in_l) | (bsig & in_s), index=c.index)
    return l_, s_, close_all


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, ca = _signals(bars_df, p)
    ex = ca & ~le & ~se                       # the close_all only closes a position the entries leave unchanged
    return le & ~se, ex, se, ex.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    sl_f = float(p["sl"]) * c.shift(1) / o   # 3.5 % of the signal close from the entry
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
