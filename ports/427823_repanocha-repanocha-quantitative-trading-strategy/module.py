"""RePaNoCHa V4, broker days: a range-filter breakout (price beyond the filter's band with the filter
rising) confirmed by Parabolic SAR, a rising T3, RSI above 52, a positive MACD histogram and no
opposing ADX trend goes long; the mirror goes short. Positions close on the source's "X" conditions
(a counter-trend ADX + SAR + T3 turn, or the opposite signal). The tick-scaled dynamic trailing stop is
pending (not expressible).
Port of FMZ strategy #427823 "RePaNoCHa Quantitative Trading Strategy" (RePaNoCHa V4 [Backtest]).

FMZ source id: 427823

Source
    https://www.fmz.com/strategy/427823 (PineScript v4, FMZ last modified 2023-09-25 18:29:33).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 218-777), src hlc3, T3 3 / 0.4, range filter 23 / 1.5, ADX 12 / 8,
SAR 0.07 / 0.05 / 0.15, RSI 14 / 52, MACD 10 / 19 / 9, trail 0.5 % / 0.25-1 %, stop off
    longCond = high > hband and upward > 0 and not (DI- > DI+ and ADX > 8) and SAR < close and T3 rising
               and RSI > 52 and hist > 0 (shortCond mirrors); XlongCond / XshortCond: counter-trend turns
    longCondition = longCond and CondIni_long[1] == -1 (state machines CondIni_long / _short / X)
    entry long on longCondition, short on shortCondition (pyramiding 100)
    close_all on Final_XlongCondition or Final_XshortCondition (stop loss off by default)
    strategy.exit trail_points / trail_offset = price distances x 2 ("pips correction") in ticks

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * All the state machines are ported as written, including the trailing-stop flags (long_ts /
      short_ts), which feed CondIni_long / _short and the X closes. `timenow > time + ...` is true on
      every historical bar (the delay snapshot logic only affects ts_delay, which reaches no order).
    * Division by zero (the entry price is 0 before the first signal) is na, as in Pine.
    * The trailing exit is not expressible (its offset grows with the profit and its distances are
      tick counts scaled by the "pips correction" 2): mark trailing_stop_pending; not ported. The
      anti-liquidation flags reach no order. Decision owed: the intended trail.
    * Adds (pyramiding 100) are sizing: one unit held. An entry and a same-bar close_all: the entry
      wins (house convention). Position BOTH (default). The start-year filter is dropped.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d). REVERSAL INTENDED.

Admission criteria
    1 fits the interface: PASS, bar-close orders; timenow is constant-true on history.
    2 generic: PASS, indicator levels and percentages (the pending trail's tick scaling aside).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, pyramiding 100 and the trail quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the T3 "volume factor" is a smoothing constant, not volume.
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427823_repanocha_v4"
FAMILY = "range_filter_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [23, 46],
    "mult": [1.5, 2.5],
    "adx_th": [8, 20],
}
DEFAULT_PARAMS = {"t3_len": 3, "a1": 0.4, "per": 23, "mult": 1.5, "adx_len": 12, "adx_th": 8,
                  "sar_start": 0.07, "sar_inc": 0.05, "sar_max": 0.15, "rsi_len": 14, "rsi_c": 52,
                  "fast": 10, "slow": 19, "signal": 9, "tsi": 0.5, "ts_low": 0.25, "ts_high": 1.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
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


def _ema(x, n):
    return x.ewm(span=n, adjust=False, ignore_na=True).mean().where(x.notna())


def _pmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _pmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _nz(x):
    return 0.0 if np.isnan(x) else x


def _t3(src, n, a):
    e1 = _ema(src, n); e2 = _ema(e1, n); e3 = _ema(e2, n)
    e4 = _ema(e3, n); e5 = _ema(e4, n); e6 = _ema(e5, n)
    c1 = -a ** 3
    c2 = 3 * a * a + 3 * a ** 3
    c3 = -6 * a * a - 3 * a - 3 * a ** 3
    c4 = 1 + 3 * a + a ** 3 + 3 * a * a
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


def _range_filter(src, per, mult):
    rng = (_ema(_ema((src - src.shift(1)).abs(), per), 2 * per - 1) * mult).to_numpy()
    s = src.to_numpy(dtype=float)
    m = len(s)
    f = np.full(m, np.nan)
    upw, dnw = np.zeros(m), np.zeros(m)
    for i in range(m):
        f1 = _nz(f[i - 1]) if i else 0.0
        if s[i] > f1:
            f[i] = f1 if (s[i] - rng[i]) < f1 else s[i] - rng[i]
        else:
            f[i] = f1 if (s[i] + rng[i]) > f1 else s[i] + rng[i]
        fp = f[i - 1] if i else np.nan
        u1 = upw[i - 1] if i else 0.0
        d1 = dnw[i - 1] if i else 0.0
        upw[i] = u1 + 1 if f[i] > fp else (0.0 if f[i] < fp else u1)
        dnw[i] = d1 + 1 if f[i] < fp else (0.0 if f[i] > fp else d1)
    return rng, f, upw, dnw


def _adx(h, lo, c, n):
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    s_tr = s_p = s_m = 0.0
    dip, dim, dx = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        c1 = cv[i - 1] if i else 0.0
        h1 = hv[i - 1] if i else 0.0
        l1 = lv[i - 1] if i else 0.0
        tr = max(hv[i] - lv[i], abs(hv[i] - c1), abs(lv[i] - c1))
        dmp = max(hv[i] - h1, 0) if hv[i] - h1 > l1 - lv[i] else 0.0
        dmm = max(l1 - lv[i], 0) if l1 - lv[i] > hv[i] - h1 else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        with np.errstate(divide="ignore", invalid="ignore"):
            dip[i] = s_p / s_tr * 100 if s_tr else np.nan
            dim[i] = s_m / s_tr * 100 if s_tr else np.nan
            tot = dip[i] + dim[i]
            dx[i] = abs(dip[i] - dim[i]) / tot * 100 if tot else np.nan
    adx = pd.Series(dx).rolling(n).mean().to_numpy()
    return dip, dim, adx


def _sar(h, lo, st, inc, mx):
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    P, EP, SAR, AF = np.ones(m), np.full(m, np.nan), np.full(m, np.nan), np.full(m, st)
    for i in range(m):
        h1 = hv[i - 1] if i else np.nan
        l1 = lv[i - 1] if i else np.nan
        p, ep, sar, af = 1.0, _pmax(hv[i], h1), _pmin(lv[i], l1), st
        epn, afn = 0.0, st
        if i == 0:
            P[i], EP[i], SAR[i], AF[i] = p, ep, sar, af
            continue
        pp, ep1, sar1, af1 = P[i - 1], EP[i - 1], SAR[i - 1], AF[i - 1]
        epn = _pmax(hv[i], ep1) if pp == 1 else _pmin(lv[i], ep1)
        afn = min(mx, af1 + inc) if (not np.isnan(epn) and not np.isnan(ep1) and epn != ep1) else af1
        up_x = sar1 + af1 * (epn - sar1)
        dn_x = sar1 - af1 * (sar1 - epn)
        if pp == 1 and up_x <= lv[i]:
            p, sar, ep, af = 1.0, sar1 + afn * (epn - sar1), epn, afn
        elif pp == 1 and up_x > lv[i]:
            if lv[i] >= sar1:
                p, sar, ep, af = 1.0, lv[i], epn, afn
            else:
                p, sar, ep, af = -1.0, _pmax(hv[i], ep1), _pmin(lv[i], l1), st
        elif pp == -1 and dn_x >= hv[i]:
            p, sar, ep, af = -1.0, sar1 - afn * (sar1 - epn), epn, afn
        elif pp == -1 and dn_x < hv[i]:
            if hv[i] <= sar1:
                p, sar, ep, af = -1.0, hv[i], epn, afn
            else:
                p, sar, ep, af = 1.0, _pmin(lv[i], ep1), _pmax(hv[i], h1), st
        P[i], EP[i], SAR[i], AF[i] = p, ep, sar, af
    return SAR


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0)
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + c) / 3
    t3 = _t3(src, int(p["t3_len"]), float(p["a1"]))
    t3r, t3f = (t3 > t3.shift(1)).to_numpy(), (t3 < t3.shift(1)).to_numpy()
    rng, filt, upw, dnw = _range_filter(src, int(p["per"]), float(p["mult"]))
    hband, lband = filt + rng, filt - rng
    dip, dim, adx = _adx(h, lo, c, int(p["adx_len"]))
    sar = _sar(h, lo, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    macd = _ema(src, int(p["fast"])) - _ema(src, int(p["slow"]))
    hist = (macd - _ema(macd, int(p["signal"]))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    th = float(p["adx_th"])
    tsi, lp_, hp_ = p["tsi"] / 100, float(p["ts_low"]), float(p["ts_high"])
    with np.errstate(invalid="ignore"):
        adx_up = (dip > dim) & (adx > th)
        adx_dn = (dip < dim) & (adx > th)
        long_cond = (hv > hband) & (upw > 0) & ~adx_dn & (sar < cv) & t3r & (rsi > p["rsi_c"]) & (hist > 0)
        short_cond = (lv < lband) & (dnw > 0) & ~adx_up & (sar > cv) & t3f & (rsi < p["rsi_c"]) & (hist < 0)
        xl_cond = (lv < hband) & (dnw > 0) & adx_up & (sar > cv) & t3f
        xs_cond = (hv > lband) & (upw > 0) & adx_dn & (sar < cv) & t3r

    def ts_dyn(x):
        return np.nan if np.isnan(x) else max(((hp_ - lp_) / 9.5) * (x - 0.5) + lp_, lp_)

    def ratio(a, b):
        return np.nan if b == 0 else abs((a - b) / b * 100)

    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    ci_l = ci_s = ci_x = 0
    ci_xl = ci_xs = 0
    lo_l = lo_s = 0.0                       # last_open_long / shortCondition (closes)
    t_l = t_s = t_xl = t_xs = 0             # last_* "time" (bar number + 1; 0 = none)
    t_lts = t_sts = 0
    long_ts = short_ts = False
    prev_lc = prev_sc = False               # longCondition[1], shortCondition[1]
    pos = 0
    for i in range(m):
        stamp = i + 1
        lc_, sc_ = bool(long_cond[i]), bool(short_cond[i])
        xl_, xs_ = bool(xl_cond[i]), bool(xs_cond[i])
        new_ci_l = 1 if lc_ else (-1 if sc_ else ci_l)
        new_ci_s = 1 if lc_ else (-1 if sc_ else ci_s)
        lcond = lc_ and ci_l == -1
        scond = sc_ and ci_s == 1
        new_ci_x = 1 if xl_ else (-1 if xs_ else ci_x)
        xlcond = xl_ and ci_x == -1
        xscond = xs_ and ci_x == 1
        lo_l = cv[i] if lcond else lo_l
        lo_s = cv[i] if scond else lo_s
        t_s_prev, t_l_prev, t_xl_prev, t_xs_prev = t_s, t_l, t_xl, t_xs
        t_l = stamp if lcond else t_l
        t_s = stamp if scond else t_s
        in_l, in_s = t_l > t_s, t_s > t_l
        t_xl = stamp if xlcond else t_xl
        t_xs = stamp if xscond else t_xs
        in_lx, in_sx = t_l > t_xl, t_s > t_xs
        ts = ts_dyn(ratio(hv[i], lo_l)) if in_l else ts_dyn(ratio(lv[i], lo_s))
        f = np.nan if np.isnan(ts) else ts / 100
        # long_ts / short_ts (var bool; keep the old value when no branch assigns)
        with np.errstate(invalid="ignore"):
            thr_l = lo_l * (1 + tsi) * (1 + f)
            if hv[i] > thr_l:
                long_ts = (hv[i] >= cv[i] * (1 + f)) and (hv[i] >= lo_l * (1 + tsi)) and \
                    (hv[i] >= hband[i] * (1 + f)) and in_l and in_lx and not lcond
            elif hv[i] <= thr_l:
                long_ts = (hv[i] >= cv[i] * (1 + f)) and (hv[i] >= lo_l * (1 + tsi)) and \
                    (cv[i] >= lo_l * (1 + tsi)) and (hv[i] >= hband[i] * (1 + f)) and in_l and in_lx and not lcond
            if (hv[i] < cv[i] * (1 + f)) and (hv[i] > thr_l) and (hv[i] >= hband[i] * (1 + f)):
                long_ts = in_l and in_lx and not lcond
            thr_s = lo_s * (1 - tsi) * (1 - f)
            if lv[i] < thr_s:
                short_ts = (lv[i] <= cv[i] * (1 - f)) and (lv[i] <= lo_s * (1 - tsi)) and \
                    (lv[i] <= lband[i] * (1 - f)) and in_s and in_sx and not scond
            elif lv[i] >= thr_s:
                short_ts = (lv[i] <= cv[i] * (1 - f)) and (lv[i] <= lo_s * (1 - tsi)) and \
                    (cv[i] <= lo_s * (1 - tsi)) and (lv[i] <= lband[i] * (1 - f)) and in_s and in_sx and not scond
            if (lv[i] > cv[i] * (1 - f)) and (lv[i] < thr_s) and (lv[i] <= lband[i] * (1 - f)):
                short_ts = in_s and in_sx and not scond
        f_lts = long_ts and t_l > t_lts
        f_sts = short_ts and t_s > t_sts
        t_lts = stamp if long_ts else t_lts
        t_sts = stamp if short_ts else t_sts
        if f_lts or xlcond:
            new_ci_l = -1
        if f_sts or xscond:
            new_ci_s = 1
        fl_nc = lcond and bool(adx_up[i])
        fs_nc = scond and bool(adx_dn[i])
        fl = prev_lc and not (scond and bool(adx_dn[i]))
        fs = prev_sc and not (lcond and bool(adx_up[i]))
        new_ci_xl = 1 if (f_lts or xlcond or fs) else (-1 if fl else ci_xl)
        new_ci_xs = 1 if (f_sts or xscond or fl) else (-1 if fs else ci_xs)
        fxl = ((scond and t_l > t_s_prev) or (xlcond and t_l > t_xl_prev)) and ci_xl == -1 \
            and not fs_nc and not fs
        fxs = ((lcond and t_s > t_l_prev) or (xscond and t_s > t_xs_prev)) and ci_xs == -1 \
            and not fl_nc and not fl
        # orders: entries win over a same-bar close_all
        if lcond:
            pos = 1
        elif scond:
            pos = -1
        elif fxl or fxs:
            pos = 0
        tgt[i] = pos
        ci_l, ci_s, ci_x, ci_xl, ci_xs = new_ci_l, new_ci_s, new_ci_x, new_ci_xl, new_ci_xs
        prev_lc, prev_sc = lcond, scond
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
