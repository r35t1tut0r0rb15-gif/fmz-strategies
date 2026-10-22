"""Stochastic 14 / 3 crossings in the outer bands on the EMA 20 / 50 trend side, hourly bars: K crossing over D under 15 in an up-trend goes long, crossing under D over 85 in a down-trend goes short, each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #477533 "Dual EMA Stochastic Oscillator System A Quantitative Trading Model Combining Trend Following and Momentum" (EMA + Stochastic Strategy).

FMZ source id: 477533

Source
    https://www.fmz.com/strategy/477533 (PineScript v6, FMZ last modified 2025-01-06 11:48:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 82-146), EMA 20 / 50; stochastic 14, D 3; bands 15 / 85; stop 1 %, risk-reward 2
    ema20 > ema50 and k < 15 and crossover(k, d) -> entry Buy, exit(stop = close x 0.99, limit = close x 1.02);  ema20 < ema50 and k > 85 and crossunder(k, d) -> entry Sell, exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close: the opening signal's levels are ported,
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256); a repeat signal inside a trade re-sends it and is not followed (as #434428,
      mark trailing_stop_pending). A zero stochastic range gives na (no signal). REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, stochastic band crossings on the EMA trend side with a bracket.
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

NAME = "fmz_477533_stoch14_band_cross_ema20_50_trend_pct_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stoch_k": [14, 21],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"stoch_k": 14, "rr": 2.0, "stoch_d": 3, "sl_pct": 0.01, "ema_short": 20, "ema_long": 50}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["stoch_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100 * (c - ll) / (hh - ll).where(hh > ll)
    d = k.rolling(int(p["stoch_d"])).mean()
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    le = (es > el) & (k < 15) & (k > d) & (k.shift(1) <= d.shift(1))
    se = (es < el) & (k > 85) & (k < d) & (k.shift(1) >= d.shift(1))
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
