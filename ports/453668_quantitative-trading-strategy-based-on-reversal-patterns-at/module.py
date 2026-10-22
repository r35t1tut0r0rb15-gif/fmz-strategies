"""Reversal candles at the 50-bar extremes, 2-hour bars: a hammer, a (bearish) engulfing or a doji with the low within 0.01 % of the 50-bar low goes long, with a stop 1 % under the bar's low and a 3 % target; the same candles at the 50-bar high go short (stop 1 % over the high); reversing.
Port of FMZ strategy #453668 "Quantitative Trading Strategy Based on Reversal Patterns at Support and Resistance Levels" (Reversal Patterns at Support and Resistance).

FMZ source id: 453668

Source
    https://www.fmz.com/strategy/453668 (PineScript v5, FMZ last modified 2024-06-07 16:45:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-177), support / resistance lowest / highest 50 (current bar included); tolerance 0.01 %; stop 1 % beyond the bar's extreme; target 3 % of the close; 100 % of equity
    (hammer or engulfing or doji) and low <= lowest(low, 50) x 1.0001 -> entry Long, exit(stop = low x 0.99, limit = close x 1.03)
    (the same) and high >= highest(high, 50) x 0.9999 -> entry Short, exit(stop = high x 1.01, limit = close x 0.97)

Interpretation choices (Pine rules in SURVEY_README.md)
    * isEngulfing() holds two expressions on separate lines and returns the last, so it is the
      bearish engulfing test only, as written. The levels are fixed on the signal bar: ported as
      fractions of the signal close (1 - 0.99 x low / close for the long stop, 1.01 x high / close - 1
      for the short's, 0.03 for both targets), read at the fill bar from the signal bar. A bar at both
      extremes ends short (the later call wins, as #437773). A repeat signal inside a trade re-issues
      the levels, which stops() cannot express: the opening levels are kept and the module is marked
      trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 2-hour bars: mark coarse_bar_stop. The 100 % of equity is sizing. FREQ = "2h" from
      the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-bar levels as fractions; re-issued levels pending (mark).
    2 generic: PASS, reversal candles at range extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_453668_reversal_candles_at_50bar_extremes_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [50, 20],
    "sl_pct": [0.01, 0.02],
    "tp_pct": [0.03, 0.05],
}
DEFAULT_PARAMS = {"lookback": 50, "sl_pct": 0.01, "tp_pct": 0.03, "tol": 0.0001}


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
    lower_wick = np.where(o > c, np.where(lo < c, c - lo, o - lo), np.where(lo < o, o - lo, c - lo))
    upper_wick = h - np.maximum(o, c)
    hammer = (pd.Series(lower_wick, index=c.index) > body * 2) & (upper_wick < body)
    engulf = (c.shift(1) > o.shift(1)) & (c < o) & (c < o.shift(1)) & (o > c.shift(1))
    doji = body <= (h - lo) * 0.1
    pat = hammer | engulf | doji
    n = int(p["lookback"])
    t = float(p["tol"])
    buy = pat & (lo <= lo.rolling(n).min() * (1 + t))
    sell = pat & (h >= h.rolling(n).max() * (1 - t))
    return buy & ~sell, sell


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    buy, sell = _signals(bars_df, p)
    k = float(p["sl_pct"])
    sl = pd.Series(np.nan, index=c.index)
    sl = sl.mask(buy, 1 - lo * (1 - k) / c).mask(sell, h * (1 + k) / c - 1)
    tp = pd.Series(np.nan, index=c.index).mask(buy | sell, float(p["tp_pct"]))
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
