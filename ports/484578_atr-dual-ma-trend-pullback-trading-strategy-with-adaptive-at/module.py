"""EMA 10 / 50 trend pullbacks, 2-hour bars: after a bar closing under the EMA 10 but holding above the EMA 50 in an uptrend, a bar opening under and closing over the EMA 10 goes long; the mirror goes short; each with a 2 ATR 14 stop and a 2R target from the signal close; reversing.
Port of FMZ strategy #484578 "双均线趋势回调自适应ATR止盈止损量化交易策略-Dual-MA-Trend-Pullback-Trading-Strategy-with-Adaptive-ATR-Based-Risk-Management" (Pullback Strategy).

FMZ source id: 484578

Source
    https://www.fmz.com/strategy/484578 (PineScript v5, FMZ last modified 2025-03-03 09:49:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 190-245), EMA 10 / 50; ATR 14; stop 2 ATR; target 2R; 100 % of equity, capital 100000, commission 0.01 %
    pullback = ema10 > ema50 and close < ema10 and low > ema50;  long = ema10 > ema50 and pullback[1] and open < ema10 and close > ema10 -> entry Long + exit(stop = close - 2 atr, limit = close + 4 atr)
    rally = ema10 < ema50 and close > ema10 and high < ema50;  short = ema10 < ema50 and rally[1] and open > ema10 and close < ema10 -> entry Short + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while held re-sends
      the bracket; stops() keeps the first, so the repeat case is marked trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The 100 % of equity size and
      the capital are sizing; the commission is a cost (the house cost model applies). FREQ = "2h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, EMA trend pullbacks with an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484578_ema10_50_pullback_reclaim_atr2_2r_bracket_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_ma_length": [10, 20],
    "sl_multiplier": [2.0, 1.5],
}
DEFAULT_PARAMS = {"fast_ma_length": 10, "sl_multiplier": 2.0, "slow_ma_length": 50, "atr_period": 14}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["fast_ma_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_ma_length"]), adjust=False).mean()
    up, dn = f > s, f < s
    pull = up & (c < f) & (lo > s)
    rally = dn & (c > f) & (h < s)
    le = up & pull.shift(1, fill_value=False) & (o < f) & (c > f)
    se = dn & rally.shift(1, fill_value=False) & (o > f) & (c < f)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, int(p["atr_period"])) * float(p["sl_multiplier"])
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
