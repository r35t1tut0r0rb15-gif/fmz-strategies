"""Fibonacci retracement candles against the last 4-hour range, 2-minute bars: a green candle closing over the 61.8 % level and under the 50-bar high of the 4-hour highs goes long, a red candle under the 78.6 % level and over the low goes short, each with a 1 % stop and 2 % target (risk-reward 2) from the signal close; reversing.
Port of FMZ strategy #474708 "Multi Timeframe Fibonacci Retracement with Trend Breakout Trading Strategy" (Fibonacci Swing Trading Bot).

FMZ source id: 474708

Source
    https://www.fmz.com/strategy/474708 (PineScript v5, FMZ last modified 2024-12-11 17:32:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-140), Fibonacci 0.618 / 0.786; risk-reward 2; stop 1 %; analysis timeframe "240"
    hh = highest(security("240", high), 50);  ll = lowest(security("240", low), 50);  fib618 = hh - (hh - ll) x 0.618;  fib786 = hh - (hh - ll) x 0.786;  close > open and close > fib618 and close < hh -> entry Buy + exit(stop = close x 0.99, limit = close x 1.02);  close < open and close < fib786 and close > ll -> entry Sell + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 4-hour request (no lookahead) is the last 4-hour bar completed by the chart bar's close (as
      #440503), built in precompute from UTC-aligned 4-hour blocks; the 50-bar extremes run over the
      2-minute samples of it, as written (#471719). The bracket is sent on every signal bar from its
      close: the opening signal's levels are ported, sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256); the re-sends of repeat signals are
      not followed (as #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed 4-hour values; signal-bar bracket as fractions of the fill.
    2 generic: PASS, retracement-level candles with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_474708_fib618_786_4h_range_candles_bracket_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fib1": [0.618, 0.5],
    "sl_pct": [0.01, 0.005],
}
DEFAULT_PARAMS = {"fib1": 0.618, "fib2": 0.786, "sl_pct": 0.01, "rr": 2.0, "lookback": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    h4 = _resample(raw_1m_df, "4h")
    ends = (h4.index + pd.Timedelta(hours=4)).asi8
    closes = (bars.index + pd.Timedelta(minutes=2)).asi8
    k = np.searchsorted(ends, closes, side="right") - 1     # last 4-hour bar completed by the chart close
    ok = k >= 0
    hv, lv = np.full(len(bars), np.nan), np.full(len(bars), np.nan)
    hv[ok] = h4["high"].to_numpy(dtype=float)[k[ok]]
    lv[ok] = h4["low"].to_numpy(dtype=float)[k[ok]]
    bars["htf_high"], bars["htf_low"] = hv, lv
    return bars


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["lookback"])
    hh = bars_df["htf_high"].rolling(n).max()
    ll = bars_df["htf_low"].rolling(n).min()
    f1 = hh - (hh - ll) * float(p["fib1"])
    f2 = hh - (hh - ll) * float(p["fib2"])
    le = (c > o) & (c > f1) & (c < hh)
    se = (c < o) & (c < f2) & (c > ll)
    sp = float(p["sl_pct"])
    tp = sp * float(p["rr"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
