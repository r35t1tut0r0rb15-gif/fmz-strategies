"""Bollinger 20 / 2 extremes with a 10-bar range bracket, 4-hour bars: after a bar that opened and closed under the lower
band, go long with the stop at the 10-bar low and the target at the 10-bar high; after a bar that opened above the upper
band and closed above the current upper band, go short with the stop at the 10-bar high and the target at the 10-bar low.
Port of FMZ strategy #434428 "Reversal-Bollinger-Bands-Strategy反转波动带策略" (Bulle de bollinger).

FMZ source id: 434428

Source
    https://www.fmz.com/strategy/434428 (PineScript v4, FMZ last modified 2023-12-06 11:20:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 103-130), SMA 20, stdev 20 x 2; stop / target = lowest(10) / highest(10) of the signal bar
    open[1] < lwr[1] and close[1] < lwr[1] -> entry long, exit(stop = lowest(10), limit = highest(10))
    open[1] > upr[1] and close[1] > upr -> entry short, exit(stop = highest(10), limit = lowest(10))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the signal bar (its 10-bar low / high, the bar included) and are ported
      as fractions of the signal close, shifted one bar inside stops() (re-based on the fill). A
      signal whose stop is not beyond the close (no risk) places no entry; a target not beyond the
      close is dropped.
    * A repeated signal while in the trade re-issues strategy.exit with that bar's levels, so the
      levels can move after entry: stops() cannot express it (mark trailing_stop_pending); the port
      keeps the opening signal's levels. The short test reads the current upper band, as written.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 4-hour bars: mark coarse_bar_stop. stdev is the population one. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-issued levels approximated).
    2 generic: PASS, Bollinger extremes and range levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434428 (2 members, best partner #435515, Jaccard 0.963); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434428_bollinger_extreme_range_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_len": [20, 40],
    "range_len": [10, 20],
}
DEFAULT_PARAMS = {"bb_len": 20, "mult": 2.0, "range_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["bb_len"])
    mdl = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0)
    upr, lwr = mdl + float(p["mult"]) * dev, mdl - float(p["mult"]) * dev
    r = int(p["range_len"])
    ll, hh = lo.rolling(r).min(), h.rolling(r).max()
    l_sl, l_tp = ((c - ll) / c).to_numpy(), ((hh - c) / c).to_numpy()
    s_sl, s_tp = ((hh - c) / c).to_numpy(), ((c - ll) / c).to_numpy()
    with np.errstate(invalid="ignore"):
        le = ((o.shift(1) < lwr.shift(1)) & (c.shift(1) < lwr.shift(1))).to_numpy() & (l_sl > 0)
        se = ((o.shift(1) > upr.shift(1)) & (c.shift(1) > upr)).to_numpy() & (s_sl > 0)
        sl = np.where(le, l_sl, np.where(se, s_sl, np.nan))
        tp = np.where(le, l_tp, np.where(se, s_tp, np.nan))
        tp = np.where(tp > 0, tp, np.nan)
    return le, se, sl, tp


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
