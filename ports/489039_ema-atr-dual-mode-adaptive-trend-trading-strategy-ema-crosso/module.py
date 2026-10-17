"""Adaptive EMA 3 / 8 crosses (trend or counter-trend by RSI strength), spaced 72 bars, from flat, with an ATR bracket,
broker days: when RSI 14 is far from 50 (trending), an EMA 3 / 8 cross with the EMA 55 side and SMA 5 / 20 trend
enters with the trend; when it is near 50, a cross against the EMA 55 side enters counter-trend; each trade has a
1.2 ATR stop and a 2 ATR target.
Port of FMZ strategy #489039 "双模式自适应趋势交易策略EMA交叉结合ATR波动率风险管理系统-Dual-Mode-Adaptive-Trend-Trading-Strategy-EMA-Crossover-with-ATR-Volatility-Based-Risk-Management-System" (DOGE/USDT 5X Adaptive Trend Strategy).

FMZ source id: 489039

Source
    https://www.fmz.com/strategy/489039 (PineScript v6, FMZ last modified 2025-04-01 14:20:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 238-320), EMA 3 / 8 / 55, ATR 14, 72 bars between trades, RSI 14 strength 0.3
    trending = |rsi - 50| / 50 > 0.3;  up / downtrend = SMA 5 vs SMA 20
    trend long = cross up, close > ema55, uptrend;  counter long = cross up, close < ema55 (shorts mirrored)
    valid = (trending ? trend entry : counter entry) and bar_index - lastTrade >= 72 and position == 0
    entry + exit(stop = close -+ 1.2 ATR, limit = close +- 2 ATR); lastTrade = bar_index

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop = 1.2 x ATR / close, tp_stop = 2 x ATR / close, shifted
      one bar inside stops(), re-based on the fill (house rule).
    * Entries only from flat: simulate() follows the house bracket on bars (from the fill bar), as the desktop's
      flat-only bracket ports. The spacing is 72 BARS as written (the input says minutes; on daily bars 72 days).
      A long wins over a short on one bar (source order). Opposite entries cannot occur.
    * Leverage and the risk-based quantity are sizing. Stop module: portfolio_kwargs {} (D4). Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, EMAs, SMAs, RSI and ATR multiples.
    3 crypto-exchange-only: no ("DOGE/USDT" in the title and the exchange pair only).
    4 signals only: leverage and the 1 %-risk quantity quoted; the bracket ported via stops() and quoted.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489039_adaptive_ema_cross_spaced_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trade_interval": [72, 5],
    "use_adaptive": [True, False],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 8, "trend": 55, "atr_period": 14, "trade_interval": 72, "sl_mult": 1.2,
                  "tp_mult": 2.0, "use_adaptive": True, "adaptive_period": 14}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    et = c.ewm(span=int(p["trend"]), adjust=False).mean()
    xu = (ef > es) & (ef.shift(1) <= es.shift(1))
    xd = (ef < es) & (ef.shift(1) >= es.shift(1))
    trending = ((_rsi(c, int(p["adaptive_period"])) - 50).abs() / 50) > 0.3
    s5, s20 = c.rolling(5).mean(), c.rolling(20).mean()
    up_t, dn_t = s5 > s20, s5 < s20
    if p["use_adaptive"]:
        lsig = (trending & xu & (c > et) & up_t) | (~trending & xu & (c < et))
        ssig = (trending & xd & (c < et) & dn_t) | (~trending & xd & (c > et))
    else:
        lsig, ssig = xu, xd
    lsig, ssig = lsig.to_numpy(dtype=bool), ssig.to_numpy(dtype=bool)
    frac = (_atr(bars_df, int(p["atr_period"])) / c).to_numpy(dtype=float)
    sl_f, tp_f = p["sl_mult"] * frac, p["tp_mult"] * frac
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_, last = 0, -1, np.nan, np.nan, 0
    gap = int(p["trade_interval"])
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and i - last >= gap and not np.isnan(sl_f[i]) and i + 1 < m:
            if lsig[i]:
                le[i], pos, entry_i, s_, t_, last = True, 1, i + 1, sl_f[i], tp_f[i], i
            elif ssig[i]:
                se[i], pos, entry_i, s_, t_, last = True, -1, i + 1, sl_f[i], tp_f[i], i
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_period"])) / bars_df["close"]
    return {"sl_stop": (p["sl_mult"] * frac).shift(1), "tp_stop": (p["tp_mult"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
