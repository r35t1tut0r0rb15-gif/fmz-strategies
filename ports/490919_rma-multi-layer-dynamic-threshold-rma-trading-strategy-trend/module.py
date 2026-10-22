"""RMA 9 / 21 / 50 stacks with the close crossing the RMA 21, RSI 8 on the same side of 50 and a break of the previous bar's extreme, hourly bars: the bullish cross goes long with the RMA 50 as target and a 10-tick stop (read as 0.05 %), the bearish cross goes short with the mirror; reversing.
Port of FMZ strategy #490919 "多层动态阈值RMA量化交易策略趋势与动量协同优化方法-Multi-Layer-Dynamic-Threshold-RMA-Trading-Strategy-Trend-and-Momentum-Synergy-Optimization" (RMA Strategy - Weekly Dynamic Thresholds).

FMZ source id: 490919

Source
    https://www.fmz.com/strategy/490919 (PineScript v5, FMZ last modified 2025-04-17 14:44:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-234), RMA 9 / 21 / 50; RSI 8; SL 10 ticks; TP at the RMA 50; thresholds (plots only)
    fast > mid > slow and crossover(close, mid) and rsi > 50 and close > high[1] -> entry Long + exit(limit = slowRMA, stop = close - 10 ticks);  mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tick stop is read as a percent at the header coin's price (TRX about 0.2 with tick 0.00001: 10
      ticks = 0.0001 = 0.05 %; C2 ADAPT, as #458242). The target is the RMA 50 on the signal bar, which in a
      bullish stack sits under the price, so the long's limit is marketable at the fill and closes it one bar
      late (as #458256), as written. A later same-side signal while held re-sends the bracket; the port
      keeps the opening levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses
      (REVERSAL INTENDED). Its DG490919 partner #491034 is read on its own. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; RMA / tick bracket as fractions of the fill.
    2 generic: ADAPT, the tick stop read as a percent at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG490919 (2 members, best partner #491034, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_490919_rma9_21_50_stack_mid_cross_rma50_target_tick_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.05, 0.5],
    "midLen": [21, 34],
}
DEFAULT_PARAMS = {"sl_pct": 0.05, "midLen": 21, "fastLen": 9, "slowLen": 50, "rsiLen": 8}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f, m, s = _rma(c, int(p["fastLen"])), _rma(c, int(p["midLen"])), _rma(c, int(p["slowLen"]))
    r = _rsi(c, int(p["rsiLen"]))
    le = (f > m) & (m > s) & (c > m) & (c.shift(1) <= m.shift(1)) & (r > 50) & (c > h.shift(1))
    se = (f < m) & (m < s) & (c < m) & (c.shift(1) >= m.shift(1)) & (r < 50) & (c < lo.shift(1))
    q = float(p["sl_pct"]) / 100
    lvl = {"l_sl": c * (1 - q), "l_tp": s, "s_sl": c * (1 + q), "s_tp": s}
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
