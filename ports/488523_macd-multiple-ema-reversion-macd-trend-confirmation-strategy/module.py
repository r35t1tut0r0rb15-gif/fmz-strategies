"""MACD 12 / 26 / 9 signal crossings with the EMA 20 / 250 side and the EMA 2 between the EMA 300 and EMA 100, hourly bars: the up-cross goes long, the down-cross goes short, each with a 5 ATR 14 stop and a 1.5 R target from the signal close; reversing.
Port of FMZ strategy #488523 "多重均线回归MACD趋势确认策略-Multiple-EMA-Reversion-MACD-Trend-Confirmation-Strategy" (Price Near 200 EMA).

FMZ source id: 488523

Source
    https://www.fmz.com/strategy/488523 (PineScript v5, FMZ last modified 2025-03-28 15:40:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-203), EMA 20 / 250 (2 / 100 / 300 hidden); MACD 12 / 26 / 9; ATR 14 x 5; RR 1.5; 100 % of equity
    ema20 > ema250 and ema300 < ema2 < ema100 and crossover(macd, signal) -> entry Buy + exit(limit = close + 7.5 atr, stop = close - 5 atr)
    ema20 < ema250 and ema100 < ema2 < ema300 and crossunder(macd, signal) -> entry Sell + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A later same-side signal while
      held re-sends the bracket; the port keeps the opening levels, mark trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, MACD crossings with EMA trend and pullback filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_488523_macd_cross_ema20_250_ema2_pullback_atr5_bracket_reversal"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atrMultiplier": [5.0, 2.5],
    "rrRatio": [1.5, 3.0],
}
DEFAULT_PARAMS = {"atrMultiplier": 5.0, "rrRatio": 1.5, "ema1Length": 20, "ema2Length": 250, "atrLength": 14}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    e1, e2 = ema(c, p["ema1Length"]), ema(c, p["ema2Length"])
    e3, e4, e5 = ema(c, 2), ema(c, 100), ema(c, 300)
    macd = ema(c, 12) - ema(c, 26)
    sig = ema(macd, 9)
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    le = (e1 > e2) & (e3 > e5) & (e3 < e4) & up
    se = (e1 < e2) & (e3 < e5) & (e3 > e4) & dn
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, int(p["atrLength"])) * float(p["atrMultiplier"])
    b = a * float(p["rrRatio"])
    lvl = {"l_sl": c - a, "l_tp": c + b, "s_sl": c + a, "s_tp": c - b}
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
