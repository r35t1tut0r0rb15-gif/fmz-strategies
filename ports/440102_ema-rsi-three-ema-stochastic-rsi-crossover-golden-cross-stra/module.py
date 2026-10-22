"""Stochastic-RSI crossing up with three rising EMAs, 1-hour bars, long only: the stochastic RSI K crossing over D while EMA 8 > EMA 14 > EMA 50 and the close is above EMA 8 goes long from flat, with a
stop 3 ATR(14) below and a target 2 ATR(14) above the entry.
Port of FMZ strategy #440102 "三重EMA随机RSI交叉金叉策略Three-EMA-Stochastic-RSI-Crossover-Golden-Cross-Strategy" (Stoch RSI Crossover Strat + EMA).

FMZ source id: 440102

Source
    https://www.fmz.com/strategy/440102 (PineScript v4, FMZ last modified 2024-01-26 16:07:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-237), stoch RSI 3 / 3 / 14 / 14 on close; ATR 14; EMA 8 / 14 / 50; profit factor 2, stop factor 3; date window from 2020
    k = sma(stoch(rsi, rsi, rsi, 14), 3);  d = sma(k, 3);  crossup = k > d and k[1] <= d[1];  emapos = ema8 > ema14 > ema50 and close > ema8
    crossup and emapos and opentrades < 1 -> entry Long;  in a trade: strategy.exit(stop = (avg price - 3 atr)[barsbought], limit = (avg price + 2 atr)[barsbought])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are taken on the fill bar (barsbought = 0 there) from the entry price and that bar's
      ATR; the port uses the signal bar's ATR as a fraction of its close, shifted one bar inside stops()
      and re-based on the fill (as #434998): stop 3 and target 2 ATR multiples, fixed for the trade.
      Entries only from flat (opentrades < 1). The 2020-onward date window is dropped. Long only. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, stochastic RSI, EMA alignment, ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440102_stoch_rsi_cross_three_ema_atr_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_factor": [3.0, 1.5],
    "profit_factor": [2.0, 4.0],
}
DEFAULT_PARAMS = {"stop_factor": 3.0, "profit_factor": 2.0, "smooth_k": 3, "smooth_d": 3, "rsi_len": 14,
                  "stoch_len": 14, "atr_len": 14, "ema1": 8, "ema2": 14, "ema3": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signal(bars_df, p):
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    ll, hh = r.rolling(n).min(), r.rolling(n).max()
    st = 100.0 * (r - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    e1, e2, e3 = (c.ewm(span=int(p[x]), adjust=False).mean() for x in ("ema1", "ema2", "ema3"))
    return (k > d) & (k.shift(1) <= d.shift(1)) & (e1 > e2) & (e2 > e3) & (c > e1)


def _levels(bars_df, p):
    a = (_atr(bars_df, p["atr_len"]) / bars_df["close"]).to_numpy()
    return float(p["stop_factor"]) * a, float(p["profit_factor"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sig = _signal(bars_df, p).to_numpy()
    sl, tp = _levels(bars_df, p)
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and i + 1 < m and sig[i] and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _levels(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
