"""A 14-part point score (an adaptive RSI-filter direction, a TD count, a SuperTrend 3 / 7 on a volume-price-trend shadow line, ROC 20, DMI 5, CCI 21, a Weis wave direction, close vs SMA 20, AO, momentum 14, MACD histogram direction, bull / bear power, Ichimoku base line and Hull 21), broker days: the score crossing over zero goes long, crossing under goes short; reversing.
Port of FMZ strategy #428617 "Multi indicator Combination Strategy" (Super indicator).

FMZ source id: 428617

Source
    https://www.fmz.com/strategy/428617 (PineScript v4, FMZ last modified 2023-10-07 15:34:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 184-405), VPT shadow (windows 28 / 14, EMA 5), SuperTrend 3 x ATR 7; SMA 20; AO 5 / 34; mom 14; MACD 12 / 26 / 9; bull-bear SMA 30; Ichimoku base 26; Hull 21; TD 4; ROC 20; CCI 21; DMI 5; RSI-filter 2 / 14 / 20 / 7 / 13; score SMA 1
    totalpoints = rsi(+/-3) + td(+/-2) + STT(+/-1) + Roc(+/-1) + DMI(+/-2) + CCI(+/-2) + Weis(+/-2) + smapoint(+/-1) + aopoint + mompoint + histpoint(+/-3) + bbpoint + icpoint + hmapoint(+/-2)
    crossover(sma(totalpoints, 1), 0) -> entry Long;  crossunder(..., 0) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each part is as written, including smapoint's +1 / -1 from a per-bar 0 and a points value of the
      failing side when an input is na (Pine's na comparison is false). The VPT line adds the bar's spread
      volume to its own running sum (double counting the bar, as written); a zero-range bar gives na there.
      The adaptive RSI filter's efficiency ratio mixes the close's 20-bar change with the RSI's noise, as
      written. The UO is computed but not scored. ta.rising / falling are read as above / below every one of
      the previous 4 closes. The Hull half-length 9 / 2 is taken as 4. REVERSAL INTENDED. The 100 % of
      equity size and commission are sizing / costs. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, multi-indicator point score zero crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000, commission 0.075 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VPT shadow line under the SuperTrend part and the Weis wave volume; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428617_fourteen_part_point_score_zero_cross_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_mult": [3.0, 2.0],
    "sma_len": [20, 50],
}
DEFAULT_PARAMS = {"st_mult": 3.0, "sma_len": 20, "st_period": 7}


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


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _wima(x, n):
    """The source's fn(): (src + nz(prev x (n - 1))) / n, from the first bar."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = (v[i] + (0.0 if np.isnan(prev) else prev * (n - 1))) / n
        prev = out[i]
    return pd.Series(out, index=x.index)


def _valuewhen(cond, src, k):
    """Pine valuewhen(cond, src, k): src at the k-th most recent bar where cond held (NaN before)."""
    c = np.asarray(cond, dtype=bool)
    s = np.asarray(src, dtype=float)
    out = np.full(len(c), np.nan)
    hits = []
    for i in range(len(c)):
        if c[i]:
            hits.append(s[i])
        if len(hits) > k:
            out[i] = hits[-1 - k]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    ix = c.index
    pc = c.shift(1)
    tr0 = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    tr1 = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # atr(): first bar high - low
    # VPT shadow line and its SuperTrend (STT)
    hilow = (h - lo) * 100
    sv = (c - o) * 100 * (v / hilow.where(hilow != 0))
    vp = sv + sv.fillna(0.0).cumsum()
    dvp = vp - vp.rolling(14).mean()
    shadow = dvp / dvp.rolling(28).std(ddof=0) * (h - lo).rolling(28).std(ddof=0)
    out1 = (h + shadow).where(shadow > 0, lo + shadow)
    vpt = out1.ewm(span=5, adjust=False).mean()
    atr7 = _rma(tr1, int(p["st_period"]))
    k = float(p["st_mult"])
    up_lev, dn_lev = (vpt - k * atr7).to_numpy(), (vpt + k * atr7).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    t10 = np.ones(m)
    ut_p = dt_p = np.nan
    tr_p = np.nan
    for i in range(m):
        c1 = cv[i - 1] if i else np.nan
        ut = max(up_lev[i], ut_p) if c1 > ut_p else up_lev[i]
        dt = min(dn_lev[i], dt_p) if c1 < dt_p else dn_lev[i]
        t = 1.0 if cv[i] > dt_p else (-1.0 if cv[i] < ut_p else (1.0 if np.isnan(tr_p) else tr_p))
        t10[i] = t
        ut_p, dt_p, tr_p = ut, dt, t
    stt = np.where(t10 == 1, 1, -1)
    # simple points
    sma20 = c.rolling(int(p["sma_len"])).mean()
    smap = np.where(c > sma20, 1, -1)
    hl2 = (h + lo) / 2
    ao = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    aop = np.where(ao > 0, 1, np.where(ao < 0, -1, 0))
    mom = c - c.shift(14)
    momp = np.where(mom > 0, 1, np.where(mom < 0, -1, 0))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    histp = np.where(hist > hist.shift(1), 3, -3)
    # bull / bear power
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    c1 = pc.to_numpy(dtype=float)
    hl = hv - lv
    r1 = np.where(c1 < ov, np.maximum(ov - c1, hl), hl)
    r2 = np.where(c1 > ov, np.maximum(c1 - ov, hl), hl)
    eq, hc, cl = cv == ov, hv - cv, cv - lv
    bull = np.where(eq, np.where(hc == cl, np.where(c1 > ov, np.maximum(hv - ov, cl), r1),
                                 np.where(hc > cl, np.where(c1 < ov, np.maximum(hv - c1, cl), hv - ov), r1)),
                    np.where(cv < ov, np.where(c1 < ov, np.maximum(hv - c1, cl), np.maximum(hv - ov, cl)), r1))
    bear = np.where(eq, np.where(hc == cl, np.where(c1 < ov, np.maximum(ov - lv, hc), r2),
                                 np.where(hc > cl, r2, np.where(c1 > ov, np.maximum(c1 - lv, hc), ov - lv))),
                    np.where(cv < ov, r2, np.where(c1 > ov, np.maximum(c1 - lv, hc), np.maximum(ov - lv, hc))))
    bbp = np.where(pd.Series(bull - bear, index=ix).rolling(30).mean() > 0, 1, -1)
    base = (lo.rolling(26).min() + h.rolling(26).max()) / 2
    icp = np.where(c > base, 1, -1)
    hullma = _wma(2 * _wma(c, 4) - _wma(c, 21), int(round(np.sqrt(21))))
    hmap = np.where(c > hullma, 2, -2)
    # Weis wave
    mov = np.sign(np.nan_to_num(c.diff().to_numpy()))
    rising = (c > c.shift(1).rolling(4).max()).to_numpy()
    falling = (c < c.shift(1).rolling(4).min()).to_numpy()
    vv = v.to_numpy(dtype=float)
    weis = np.full(m, -2)
    trend = wave = 0.0
    vol = np.nan
    mov_p = np.nan
    wave_p = np.nan
    for i in range(m):
        if mov[i] != 0 and mov[i] != mov_p:
            trend = mov[i]
        wv = trend if (trend != (0.0 if np.isnan(wave_p) else wave_p) and (rising[i] or falling[i])) else (0.0 if np.isnan(wave_p) else wave_p)
        vol = ((0.0 if np.isnan(vol) else vol) + vv[i]) if wv == wave_p else vv[i]
        up1, dn1 = (vol, 0.0) if wv == 1 else (0.0, vol)
        weis[i] = 2 if up1 > dn1 else -2
        mov_p, wave_p = mov[i], wv
    # TD count
    up4, dn4 = (c > c.shift(4)).to_numpy(), (c < c.shift(4)).to_numpy()
    td_, ts_ = np.zeros(m), np.zeros(m)
    for i in range(m):
        td_[i] = (td_[i - 1] + 1 if i else 1) if up4[i] else 0
        ts_[i] = (ts_[i - 1] + 1 if i else 1) if dn4[i] else 0
    tdu = td_ - _valuewhen(np.r_[False, td_[1:] < td_[:-1]], td_, 1)
    tdd = ts_ - _valuewhen(np.r_[False, ts_[1:] < ts_[:-1]], ts_, 1)
    tdp = np.where(tdu > 0, 2, np.where(tdd > 0, -2, 0))
    roc = 100 * (c - c.shift(20)) / c.shift(20)
    rocp = np.where(roc > 0, 1, -1)
    tp = c.rolling(21).mean()
    md = c.rolling(21).apply(lambda w: np.mean(np.abs(w - w.mean())), raw=True)
    cci = (c - tp) / (0.015 * md)
    ccip = np.where(cci > 0, 2, -2)
    upm, dnm = h.diff(), -lo.diff()
    trr = _rma(tr0, 5)
    plus = _fixnan(100 * _rma(upm.where((upm > dnm) & (upm > 0), 0.0), 5) / trr)
    minus = _fixnan(100 * _rma(dnm.where((dnm > upm) & (dnm > 0), 0.0), 5) / trr)
    dmip = np.where(plus - minus >= 0, 2, -2)
    # adaptive RSI-filter direction
    r11 = c.ewm(span=2, adjust=False).mean()
    r22 = (c - r11).where(c > r11, 0.0)
    r3 = (r11 - c).where(c < r11, 0.0)
    r4, r5 = _wima(r22, 14), _wima(r3, 14)
    rr = (100 - 100 / (1 + r4 / r5)).where(r5 != 0, 100.0)
    er = (c - c.shift(20)).abs() / rr.diff().abs().rolling(20).sum()
    dev = er * (rr * 2).rolling(7).std(ddof=0) + (1 - er) * (rr * 2).rolling(13).std(ddof=0)
    rv, dv = rr.to_numpy(), dev.to_numpy()
    a = np.full(m, np.nan)
    for i in range(m):
        if i < 9:
            a[i] = rv[i]
        elif rv[i] > a[i - 1] + dv[i] or rv[i] < a[i - 1] - dv[i]:
            a[i] = rv[i]
        else:
            a[i] = a[i - 1]
    a1 = np.r_[np.nan, a[:-1]]
    rsip = _fixnan(pd.Series(np.where(a > a1, 3.0, np.where(a < a1, -3.0, np.nan)), index=ix)).to_numpy()
    total = pd.Series(rsip + tdp + stt + rocp + dmip + ccip + weis + smap + aop + momp + histp + bbp + icp + hmap,
                      index=ix)
    le = (total > 0) & (total.shift(1) <= 0)
    se = (total < 0) & (total.shift(1) >= 0)
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
