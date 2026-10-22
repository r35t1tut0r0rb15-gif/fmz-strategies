"""Elephant bars, hourly bars: a candle body over 1.8 x its SMA 15 that closes within 10 % of its high or low (or a wide hammer shape) goes long when green and short when red, with a stop a fifth of the body inside the previous bar's low (high) and a target 1.8 bodies from the close; reversing.
Port of FMZ strategy #478740 "Dynamic Stop Loss Adjustment Elephant Bar Trend Following Strategy" (Estratégia Barra Elefante com Stop Dinâmico).

FMZ source id: 478740

Source
    https://www.fmz.com/strategy/478740 (PineScript v6, FMZ last modified 2025-01-17 16:24:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-221), bars for the average 15; close within 10 % of the extreme; size multiplier 1.8; target 1.8 x body; dynamic stop steps at 60 / 80 / 90 % of the target
    body > 1.8 sma(body, 15) and (close near the high / low or hammer) and green -> entry Compra + exit(stop = low[1] + body / 5, limit = close + 1.8 body);  red -> entry Venda + exit(stop = high[1] - body / 5, limit = close - 1.8 body)
    in a position: the stop / target variables step up when the CURRENT bar reaches 60 / 80 / 90 % of a target measured from its own close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar; the opening signal's levels are ported, sent as fractions
      of the fill open (a level at or through it is marketable and closed one bar late, as #458256). The
      stop / target steps only change the variables that a later signal bar re-sends; such re-sends
      inside a trade are not followed (as #434428, mark trailing_stop_pending). The once-per-bar flag is
      reset every bar and only orders a same-bar pair, which cannot occur (green / red). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, elephant-bar momentum entries with a candle-based bracket.
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

NAME = "fmz_478740_elephant_bar_body18_candle_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "size_mult": [1.8, 2.5],
    "profit_mult": [1.8, 3.0],
}
DEFAULT_PARAMS = {"size_mult": 1.8, "profit_mult": 1.8, "num_bars": 15, "close_pct": 10.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (c - o).abs()
    avg = body.rolling(int(p["num_bars"])).mean()
    upper = h - pd.concat([o, c], axis=1).max(axis=1)
    lower = pd.concat([o, c], axis=1).min(axis=1) - lo
    rng = h - lo
    q = float(p["close_pct"]) / 100
    near = (c >= h - q * rng) | (c <= lo + q * rng)
    hammer = (upper >= 2 * body) & (c >= h - rng * 0.1) & (rng > 1.5 * avg)
    inv = (lower >= 2 * body) & (c <= lo + rng * 0.1) & (rng > 1.5 * avg)
    size_ok = (body > float(p["size_mult"]) * avg) & (near | hammer | inv)
    le = size_ok & (c > o)
    se = size_ok & (c < o)
    k = float(p["profit_mult"])
    lvl = {"l_sl": lo.shift(1) + body / 5, "l_tp": c + k * body,
           "s_sl": h.shift(1) - body / 5, "s_tp": c - k * body}
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
