"""MACD 12 / 26 / 9 crossings on the far side of zero with an EMA 200 side, 1-minute bars: an up-cross below zero above the EMA goes long, a down-cross above zero below the EMA goes short, each with a 1 % stop and a 2 % target from the signal close; reversing.
Port of FMZ strategy #482872 "双向MACD动量与EMA趋势判定交易策略-Bidirectional-MACD-Momentum-and-EMA-Trend-Trading-Strategy" (Strategy with MACD and EMA).

FMZ source id: 482872

Source
    https://www.fmz.com/strategy/482872 (PineScript v5, FMZ last modified 2025-02-20 15:58:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-159), EMA 200; MACD 12 / 26 / 9; TP 2 %; SL 1 %; operation type Long & Short; 10 % of equity; MPL 2.0 notice (@DieBartDie)
    close > ema200 and crossover(macd, signal) and macd < 0 -> entry Long + exit(stop = close x 0.99, limit = close x 1.02)
    close < ema200 and crossunder(macd, signal) and macd > 0 -> entry Short + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The operation-type menu keeps its default (Long & Short). The levels are fixed at the signal close
      and sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256). A repeat signal while held re-sends the bracket from the new close; stops() keeps
      the first, so the repeat case is marked trailing_stop_pending (as #434428). An entry on the other
      side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity
      size is sizing. The MPL 2.0 notice is kept with the verbatim copy (ported, stated). FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, MACD crossings beyond zero with an EMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482872_macd12_26_9_cross_beyond_zero_ema200_pct_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_length": [200, 100],
    "tp_ratio": [2.0, 3.0],
}
DEFAULT_PARAMS = {"ema_length": 200, "tp_ratio": 2.0, "sl_ratio": 1.0, "fast_length": 12, "slow_length": 26,
                  "signal_length": 9}


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


def _signals(bars_df, p):
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    e = ema(c, p["ema_length"])
    macd = ema(c, p["fast_length"]) - ema(c, p["slow_length"])
    sig = ema(macd, p["signal_length"])
    le = (c > e) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < 0)
    se = (c < e) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (macd > 0)
    a, b = float(p["sl_ratio"]) / 100, float(p["tp_ratio"]) / 100
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
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
