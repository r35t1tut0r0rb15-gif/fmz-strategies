"""Stochastic (15, K 4, D 5) crossings in its extremes with a higher-low / lower-high check, hourly bars: %K crossing over %D under 15 with a low above the previous 5-bar low goes long, crossing under over 85 with a high below the previous 5-bar high goes short, each with a 3.7 % stop and a 1.8 % target from the signal close; reversing.
Port of FMZ strategy #482590 "Multi Timeframe Stochastic Oscillator Strategy with Trend Confirmation Trading System" (Swing Fairas Oil).

FMZ source id: 482590

Source
    https://www.fmz.com/strategy/482590 (PineScript v5, FMZ last modified 2025-02-19 10:53:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-174), Stoch 15, K 4, D 5; 85 / 15; SL 3.7 %, TP 1.8 %; "30" / "60" requests unused
    crossover(k1, d1) and k1 < 15 and low > lowest(low[1], 5) -> entry Buy + exit(stop = close x 0.963, limit = close x 1.018);  crossunder and k1 > 85 and high < highest(high[1], 5) -> entry Sell + exit (mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 30- and 60-minute stochastics are requested but feed no condition, so they are not ported. %K
      is na when the range is 0. The levels are fixed at the signal close and sent as fractions of the fill
      open (a level at or through it is marketable and closed one bar late, as #458256). A repeat signal
      while the side is held re-sends the bracket from the new close; stops() keeps the first, so the
      repeat case is marked trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close as fractions of the fill.
    2 generic: PASS, Stochastic extreme crossings with a swing check.
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

NAME = "fmz_482590_stoch15_extreme_cross_swing5_pct_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [3.7, 2.0],
    "tp_pct": [1.8, 4.0],
}
DEFAULT_PARAMS = {"sl_pct": 3.7, "tp_pct": 1.8, "length": 15, "k_smooth": 4, "d_smooth": 5,
                  "overbought": 85, "oversold": 15, "swing": 5}


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100 * (c - ll) / (hh - ll).replace(0.0, np.nan)
    k = st.rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    w = int(p["swing"])
    le = (k > d) & (k.shift(1) <= d.shift(1)) & (k < float(p["oversold"])) & (lo > lo.shift(1).rolling(w).min())
    se = (k < d) & (k.shift(1) >= d.shift(1)) & (k > float(p["overbought"])) & (h < h.shift(1).rolling(w).max())
    sl, tp = float(p["sl_pct"]) / 100, float(p["tp_pct"]) / 100
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
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
