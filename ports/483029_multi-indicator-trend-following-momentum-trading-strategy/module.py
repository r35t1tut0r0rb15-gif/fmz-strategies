"""MACD 12 / 26 / 9 crossings on the SMA 200 side with RSI 14 beyond 50 and a recent EMA 50 pullback, hourly bars: the up-cross goes long and the down-cross goes short, each with the source's bracket from the signal close (a 40 % stop and a 150 % target, as written); reversing.
Port of FMZ strategy #483029 "Multi Indicator Trend Following Momentum Trading Strategy" (Trend-Following Momentum Strategy).

FMZ source id: 483029

Source
    https://www.fmz.com/strategy/483029 (PineScript v6, FMZ last modified 2025-02-21 10:06:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-136), SMA 200; EMA 50; RSI 14; MACD 12 / 26 / 9; RR 1.5; trailing 1 % (trail_price only); 2 % of equity
    close > sma200 and crossover(macd, signal) and rsi > 50 and barssince(close < ema50) < 5 -> entry Long + exit(limit = close x (1 + 1.5), stop = close x (1 - 1 / 2.5), trail_price = close x 0.99)
    close < sma200 and crossunder(macd, signal) and rsi < 50 and barssince(close > ema50) < 5 -> entry Short + exit(limit = close x (1 - 1.5), stop = close x (1 + 1 / 2.5), trail_price = close x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written (intended version owed): the risk-reward ratio is used as a fraction of the price, so
      the long's target is 2.5 x the close and its stop 0.6 x the close; the short's stop is 1.4 x the
      close and its target a negative price that can never fill (no short target is ported).
      trail_price is passed with no trail_offset, so no trail is active (as #441084).
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while held re-sends
      the bracket; stops() keeps the first, so the repeat case is marked trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). The 2 % of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, MACD crossings with SMA / RSI / pullback filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483029_macd_cross_sma200_rsi50_ema50_pullback_rr_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_reward": [1.5, 1.0],
    "pullback_bars": [5, 10],
}
DEFAULT_PARAMS = {"risk_reward": 1.5, "pullback_bars": 5, "ma_length": 200, "ema_length": 50, "rsi_length": 14}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _bars_since(cond):
    """ta.barssince: bars since cond was last true (na before the first true)."""
    v = cond.to_numpy()
    out = np.full(len(v), np.nan)
    last = None
    for i in range(len(v)):
        if v[i]:
            last = i
        if last is not None:
            out[i] = i - last
    return pd.Series(out, index=cond.index)


def _signals(bars_df, p):
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    ma = c.rolling(int(p["ma_length"])).mean()
    e50 = ema(c, p["ema_length"])
    r = _rsi(c, int(p["rsi_length"]))
    macd = ema(c, 12) - ema(c, 26)
    sig = ema(macd, 9)
    k = int(p["pullback_bars"])
    pb_l = _bars_since(c < e50) < k
    pb_s = _bars_since(c > e50) < k
    le = (c > ma) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r > 50) & pb_l
    se = (c < ma) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r < 50) & pb_s
    rr = float(p["risk_reward"])
    s_tp = c * (1 - rr)
    lvl = {"l_sl": c * (1 - 1 / (1 + rr)), "l_tp": c * (1 + rr), "s_sl": c * (1 + 1 / (1 + rr)),
           "s_tp": s_tp.where(s_tp > 0)}
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
