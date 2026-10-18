"""Low-lag average crossing with a tick bracket, 4-hour bars: the fast delayed-DEMA line crossing its own 2-bar-delayed copy, while still above (below) the 1-bar-delayed copy, goes long (short), reversing; each trade
has a tick-sized stop (130) and target (200) re-expressed as ATR multiples.
Port of FMZ strategy #436519 "Low Lag Triple Moving Average Fast Trading Strategy" (scalping low lag tema etal).

FMZ source id: 436519

Source
    https://www.fmz.com/strategy/436519 (PineScript v4, FMZ last modified 2023-12-25 14:24:38).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 125-202), type temadelay, N 8, K 1.2, take profit 200, stop 130, trail 1 (ticks)
    temadelay: a = tema(close, 12), b = a[1], c = a[2] (tema here = 2 ema - ema(ema), a DEMA);  long = cross(a, c) and a > b;  short = cross(a, c) and a < b;  entry Long / Short with qty = floor(equity / close)
    exit(profit = 200, loss = 130, trail_points = 1) for both entries;  five other types: nkclose, ema, emadelay, fastema, tema

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick amounts (200 / 130 ticks) are re-expressed as sl_stop = k_atr x ATR / close and
      tp_stop = 1.5385 (200 / 130) x sl_stop of the signal bar, shifted one bar inside stops() (re-based on the
      fill); 0.03 is the reading (about 130 ticks of 0.1 on BTC against a 4-hour ATR near 400), 0.5 a
      volatility-sized stop. trail_points without a trail_offset starts no trailing stop. cross() is
      a crossing in either direction. REVERSAL INTENDED. The all-in quantity is sizing. FREQ = "4h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick amounts -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs and the lot formula stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436519_low_lag_ma_cross_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mav": ["temadelay", "emadelay"],
    "k_atr": [0.03, 0.5],
}
DEFAULT_PARAMS = {"mav": "temadelay", "n": 8, "k": 1.2, "k_atr": 0.03, "tp_ratio": 1.5385, "atr_len": 14}


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


def _ema(s, n):
    return s.ewm(span=int(n), adjust=False).mean()


def _tema(s, n):
    e = _ema(s, n)
    return 2 * e - _ema(e, n)          # as written: this "tema" is a DEMA


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cl = bars_df["close"]
    fast_in = cl + float(p["k"]) * (cl - cl.shift(int(p["n"])))
    mav = p["mav"]
    if mav == "nkclose":
        a = _ema(fast_in, 12)
        b, c3 = a.shift(1), a.shift(2)
    elif mav == "ema":
        a, b, c3 = _ema(cl, 12), _ema(cl, 26), _ema(cl, 55)
    elif mav == "emadelay":
        a = _ema(cl, 12)
        b, c3 = a.shift(1), a.shift(2)
    elif mav == "fastema":
        a, b, c3 = _ema(fast_in, 12), _ema(fast_in, 26), _ema(fast_in, 55)
    elif mav == "tema":
        a, b, c3 = _tema(cl, 12), _tema(cl, 26), _tema(cl, 55)
    else:
        a = _tema(cl, 12)
        b, c3 = a.shift(1), a.shift(2)
    cross = ((a > c3) & (a.shift(1) <= c3.shift(1))) | ((a < c3) & (a.shift(1) >= c3.shift(1)))
    le = (cross & (a > b)).fillna(False).astype(bool)
    se = (cross & (a < b)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * float(p["tp_ratio"])}


def portfolio_kwargs(**params):
    return {}
