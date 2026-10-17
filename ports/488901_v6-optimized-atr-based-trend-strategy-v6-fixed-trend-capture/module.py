"""SuperTrend (2, 5) side with EMA 50, RSI 45 and an ATR-expansion filter, locked out after each closed trade until the
next SuperTrend flip, with an ATR bracket, broker days: with the close above the SuperTrend and EMA 50, RSI 14 above
45 and the ATR expanding, the strategy goes long (shorts mirrored); a 2.8 ATR stop and a 5 ATR target; a repeat of the
entry condition while held closes the trade at the next open unless it is already 2 ATR in profit (the source's
break-even exit), as written.
Port of FMZ strategy #488901 "优化的基于平均真实波动范围的趋势策略v6固定趋势捕捉-Optimized-ATR-Based-Trend-Strategy-v6-Fixed-Trend-Capture" (Optimized ATR-Based Trend Strategy v6 (Fixed Trend Capture)).

FMZ source id: 488901

Source
    https://www.fmz.com/strategy/488901 (PineScript v6, FMZ last modified 2025-03-31 16:50:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 138-211), EMA 50, SuperTrend 2 / 5, ATR 14 (MA 50), RSI 14 (45), TP 5 ATR, TSL 3.5 ATR, stop 0.8 x TSL, break-even 2 ATR
    trending = atr > sma(atr, 50) x 1.01 or rising(atr, 3);  tpHit = true on a flat bar after any closed trade, false on a flip
    long = close > ema50 and close > supertrend and rsi > 45 and trending and not tpHit (shorts mirrored, rsi < 45)
    on each long bar: exit("TSL/TP", stop = close - 2.8 ATR, trail_offset = 3.5 ATR, limit = close + 5 ATR) and
    exit("BreakEven", stop = avg price + 2 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as Pine defines it (bands ratcheted on close[1]; the line is the lower band in an up-trend).
    * The bracket of the signal bar (sl_stop = 2.8 x ATR / close, tp_stop = 5 x ATR / close, shifted one bar inside
      stops(), re-based on the fill); re-issued on later signal bars with new levels: mark trailing_stop_pending.
      trail_offset without trail_points / trail_price starts no trail: inert.
    * "BreakEven" on the signal bar from flat has an na average price (inert). On a later signal bar while held its
      stop (fill + 2 ATR for a long) is above the price unless the trade is already 2 ATR ahead, so it fills at the
      next open: ported as an exit signal on such bars (simulate() follows the house bracket on bars to know the
      position); when the trade IS 2 ATR ahead the stop locks profit and moves with the ATR (pending, not emitted).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar; re-placed exits marked.
    2 generic: PASS, SuperTrend, EMA, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits ported via stops() / signals and quoted in original_sizing.txt.
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

NAME = "fmz_488901_supertrend_ema_rsi_atr_lockout_bracket"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_mult": [5.0, 3.0],
    "rsi_level": [45, 50],
}
DEFAULT_PARAMS = {"ema_len": 50, "st_factor": 2.0, "st_len": 5, "atr_len": 14, "atr_ma": 50, "tp_mult": 5.0,
                  "tsl_mult": 3.5, "stop_mult": 0.8, "be_mult": 2.0, "rsi_len": 14, "rsi_level": 45}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _pine_supertrend(bars_df, factor, n):
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    st = np.full(m, np.nan)
    pu = pl = 0.0
    prev_st = np.nan
    for i in range(m):
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        if np.isnan(atr[i]):
            pu = pl = 0.0
            continue
        if i > 0:
            lw = lw if (lw > pl or c[i - 1] < pl) else pl
            up = up if (up < pu or c[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        st[i] = lw if d == -1 else up
        prev_st, pu, pl = st[i], up, lw
    return st


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    st = pd.Series(_pine_supertrend(bars_df, float(p["st_factor"]), int(p["st_len"])), index=c.index)
    bull_st, bear_st = c > st, c < st
    flip = ((bull_st & ~bull_st.shift(1, fill_value=False)) | (bear_st & ~bear_st.shift(1, fill_value=False))).to_numpy()
    atr = _atr(bars_df, int(p["atr_len"]))
    trending = (atr > atr.rolling(int(p["atr_ma"])).mean() * 1.01) | (atr > atr.shift(1).rolling(3).max())
    rsi = _rsi(c, int(p["rsi_len"]))
    lc = ((c > ema) & bull_st & (rsi > p["rsi_level"]) & trending).to_numpy()
    sc = ((c < ema) & bear_st & (rsi < p["rsi_level"]) & trending).to_numpy()
    av = atr.to_numpy(dtype=float)
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    sl_f = p["tsl_mult"] * p["stop_mult"] * av / cv
    tp_f = p["tp_mult"] * av / cv
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    dsl, dtp = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    closed_any, tp_hit = False, False
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = ov[entry_i]
            if (pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_))) or \
               (pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_))):
                pos, closed_any = 0, True
        if pos == 0 and closed_any:
            tp_hit = True
        if flip[i]:
            tp_hit = False
        if np.isnan(sl_f[i]) or i + 1 >= m:
            continue
        held = pos != 0 and entry_i <= i
        if lc[i] and not tp_hit:
            if pos == 1 and held:
                if cv[i] < ov[entry_i] + p["be_mult"] * av[i]:       # break-even stop above the price: next open
                    lx[i], pos, closed_any = True, 0, True
            elif pos != 1:
                le[i], dsl[i], dtp[i], pos, entry_i, s_, t_ = True, sl_f[i], tp_f[i], 1, i + 1, sl_f[i], tp_f[i]
        elif sc[i] and not tp_hit:
            if pos == -1 and held:
                if cv[i] > ov[entry_i] - p["be_mult"] * av[i]:
                    sx[i], pos, closed_any = True, 0, True
            elif pos != -1:
                se[i], dsl[i], dtp[i], pos, entry_i, s_, t_ = True, sl_f[i], tp_f[i], -1, i + 1, sl_f[i], tp_f[i]
    return le, lx, se, sx, dsl, dtp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _, _ = _run(bars_df, p)
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    *_, dsl, dtp = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(dsl, index=idx).shift(1), "tp_stop": pd.Series(dtp, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
