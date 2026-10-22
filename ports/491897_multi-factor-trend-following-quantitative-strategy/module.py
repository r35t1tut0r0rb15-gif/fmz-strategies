"""Close crossings of the Parabolic SAR 0.02 / 0.02 / 0.2 with the close beyond the EMA 2, RSI 6 over 60 (under 40) and ADX 14 at least 30, broker days: the up-cross goes long, the down-cross goes short, each with a 1.5 ATR 14 stop and 3 ATR target from the signal close; reversing.
Port of FMZ strategy #491897 "Multi Factor Trend Following Quantitative Strategy" (Estrategia SAR+EMA+RSI con Alertas).

FMZ source id: 491897

Source
    https://www.fmz.com/strategy/491897 (PineScript v5, FMZ last modified 2025-04-24 17:23:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-174), SAR 0.02 / 0.02 / 0.2; EMA 2; RSI 6; ADX 14 >= 30; ATR 14 x 1.5; target 2 x the stop; risk 2 % sizing
    crossover(close, sar) and close > ema2 and rsi6 > 60 and adx >= 30 -> entry Long + exit(stop = close - 1.5 atr, limit = close + 3 atr);  mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A later same-side crossing while
      held re-sends the bracket; the port keeps the opening levels, mark trailing_stop_pending (as #434428).
      An entry on the other side reverses (REVERSAL INTENDED). ta.sar and ta.dmi follow Pine's reference
      implementations. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. The risk-sized quantity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, SAR crossings with EMA / RSI / ADX filters and an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491897_psar_cross_ema2_rsi6_adx30_atr_bracket_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adxThreshold": [30, 20],
    "atrMultiplier": [1.5, 2.5],
}
DEFAULT_PARAMS = {"adxThreshold": 30, "atrMultiplier": 1.5, "sarStart": 0.02, "sarIncrement": 0.02,
                  "sarMax": 0.2, "rsiLength": 6, "emaFastLength": 2}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sarStart"]), float(p["sarIncrement"]), float(p["sarMax"])), index=c.index)
    e2 = c.ewm(span=int(p["emaFastLength"]), adjust=False).mean()
    r = _rsi(c, int(p["rsiLength"]))
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(up.notna())
    pc = c.shift(1)
    tr_na = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trur = _rma(tr_na, 14)
    pdi, mdi = 100 * _rma(pdm, 14) / trur, 100 * _rma(mdm, 14) / trur
    ssum = pdi + mdi
    adx = _rma(100 * (pdi - mdi).abs() / ssum.where(ssum != 0), 14)
    strong = adx >= float(p["adxThreshold"])
    le = (c > sar) & (pc <= sar.shift(1)) & (c > e2) & (r > 60) & strong
    se = (c < sar) & (pc >= sar.shift(1)) & (c < e2) & (r < 40) & strong
    tr = tr_na.copy()
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, 14) * float(p["atrMultiplier"])
    lvl = {"l_sl": c - a, "l_tp": c + 2 * a, "s_sl": c + a, "s_tp": c - 2 * a}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
