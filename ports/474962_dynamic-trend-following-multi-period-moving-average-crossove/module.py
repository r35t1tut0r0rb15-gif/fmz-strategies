"""Pullbacks to the EMA 5 of lows in an SMA 21 / 89 trend, 2-hour bars: in an up-trend a close at or under the EMA 5 of lows goes long, in a down-trend a close at or over the EMA 5 of highs goes short; each position has a 25-point stop and target from its fill (fractions of 42000); reversing.
Port of FMZ strategy #474962 "Dynamic Trend Following Multi Period Moving Average Crossover Strategy" (High 5 Trading Technique).

FMZ source id: 474962

Source
    https://www.fmz.com/strategy/474962 (PineScript v5, FMZ last modified 2024-12-13 10:40:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-147), SMA 89 / 21; EMA 5 of high / low; 1 contract each for two ids; stop / target 25 points from avg; the second id trails 25 points
    longSetup and close <= ema5Low -> entry Long 1, entry Long 2;  shortSetup and close >= ema5High -> entry Short 1, Short 2;  long: exit(Long 1, stop = avg - 25, limit = avg + 25), exit(Long 2, stop = avg - 25, trail 25 / 25);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * With pyramiding 1 only the first id of a side fills ("Long 1" / "Short 1"), so the second id's
      trail never acts. The 25 points are price amounts, ported as fractions of 42000 of the fill
      (0.000595), from strategy.position_avg_price: fixed fractions, active from the fill (as #440797).
      Entries repeat while the triggers hold (ignored while held). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. The contract count
      is not ported. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fixed fractions of the fill.
    2 generic: PASS, trend pullbacks with a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: contract count stored, not ported.
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

NAME = "fmz_474962_sma21_89_trend_ema5_pullback_point_bracket_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.000595, 0.00595],
    "tp_frac": [0.000595, 0.00595],
}
DEFAULT_PARAMS = {"sl_frac": 0.000595, "tp_frac": 0.000595}


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


def simulate(bars_df, **params):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s89, s21 = c.rolling(89).mean(), c.rolling(21).mean()
    eh, el = h.ewm(span=5, adjust=False).mean(), lo.ewm(span=5, adjust=False).mean()
    up = (c > s89) & (c > s21) & (eh > s21) & (s21 > s89)
    dn = (c < s89) & (c < s21) & (el < s21) & (s21 < s89)
    le = up & (c <= el)
    se = dn & (c >= eh)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
