"""Close crossings of the SMA 200 confirmed two bars later with RSI 14 and ADX 14 over 20, broker days, long only from flat: a confirmed up-cross goes long with a 2 % target and a 1.5 ATR 14 stop from the signal close; a confirmed down-cross closes.
Port of FMZ strategy #482901 "均线动态趋势跟踪与RSI-ADX复合指标交易策略-Dynamic-Moving-Average-Trend-Following-Strategy-with-RSI-ADX-Composite-Indicators" (BTC/USD MA200 with RSI, ADX, ATR).

FMZ source id: 482901

Source
    https://www.fmz.com/strategy/482901 (PineScript v5, FMZ last modified 2025-02-27 17:27:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-137), SMA 200; RSI 14; DMI / ADX 14; ATR 14; target 2 %; stop 1.5 ATR
    crossover(close, sma200)[2] and rsi > 40 and adx > 20 and close > sma200 and no open trade -> entry Buy + exit(limit = close x 1.02, stop = close - 1.5 atr)
    crossunder(close, sma200)[2] and rsi < 60 and adx > 20 and close < sma200 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). The flat gate is followed in the
      signal loop with the bracket checked on each bar's high / low (as 449508). ta.dmi is Wilder's DMI.
      Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR / percent bracket as fractions of the fill.
    2 generic: PASS, confirmed SMA 200 crossings with RSI / ADX filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482901_sma200_cross_confirm2_rsi_adx_atr_pct_bracket_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_length": [200, 100],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"ma_length": 200, "atr_mult": 1.5, "rsi_length": 14, "dmi_length": 14, "atr_length": 14,
                  "tp_pct": 2.0}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return tr


def _adx(bars_df, n):
    h, lo = bars_df["high"], bars_df["low"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    trs = _rma(_tr(bars_df), n)
    pdi, mdi = 100 * _rma(pdm, n) / trs, 100 * _rma(mdm, n) / trs
    s = pdi + mdi
    dx = 100 * (pdi - mdi).abs() / s.where(s > 0)
    return _rma(dx, n)


def _plan(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["ma_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    adx = _adx(bars_df, int(p["dmi_length"]))
    xu = ((c > ma) & (c.shift(1) <= ma.shift(1))).shift(2, fill_value=False)
    xd = ((c < ma) & (c.shift(1) >= ma.shift(1))).shift(2, fill_value=False)
    buy = (xu & (r > 40) & (adx > 20) & (c > ma)).to_numpy()
    sell = (xd & (r < 60) & (adx > 20) & (c < ma)).to_numpy()
    atr = _rma(_tr(bars_df), int(p["atr_length"])).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    k, q = float(p["atr_mult"]), float(p["tp_pct"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_lv, tp_lv = np.full(m, np.nan), np.full(m, np.nan)
    pos = pend = out_pend = False
    sl = tp = np.nan
    for i in range(m):
        if out_pend:
            pos, out_pend = False, False
        if pend:
            pos, pend = True, False
            sl, tp = sl_lv[i - 1], tp_lv[i - 1]
            if sl >= ov[i] or tp <= ov[i]:    # marketable at the fill: closed one bar late
                lx[i], out_pend = True, True
        if pos and not out_pend and (lv[i] <= sl or hv[i] >= tp):
            pos = False                       # the bracket closes it inside the bar
        if not pos and not out_pend and buy[i] and not np.isnan(atr[i]):
            le[i], pend = True, True
            sl_lv[i], tp_lv[i] = cv[i] - k * atr[i], cv[i] * (1 + q)
        elif pos and not out_pend and sell[i]:
            lx[i], out_pend = True, True
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx), S(sl_lv), S(tp_lv)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, _, _ = _plan(bars_df, p)
    false = pd.Series(False, index=le.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_lv, tp_lv = _plan(bars_df, p)
    o = bars_df["open"]
    sl = 1 - sl_lv.shift(1) / o
    tp = tp_lv.shift(1) / o - 1
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
