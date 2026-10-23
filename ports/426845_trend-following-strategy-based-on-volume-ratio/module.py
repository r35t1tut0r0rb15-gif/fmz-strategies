"""Bull / bear volume flow (SMA 6 of up-bar volume against SMA 6 of down-bar volume) with a moving market (EMA 6 of the 12-bar rate of change beyond +/- 1 %), 3-hour bars: more bull flow goes long, more bear flow goes short, each with a 2 % stop (and a 900 % target) from the entry; reversing.
Port of FMZ strategy #426845 "Trend Following Strategy Based on Volume Ratio" (Volume Flow BF).

FMZ source id: 426845

Source
    https://www.fmz.com/strategy/426845 (PineScript v4, FMZ last modified 2023-09-14 19:53:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 139-232), MA type Simple, length 6; factor 3.1 (unused); ROC 12, EMA 6, change 2 %; SL 2 %, TP 900 % of the avg price
    long = sma(close > open ? volume : 0, 6) > sma(open > close ? volume : 0, 6) and isMoving -> entry Long;  short mirror -> entry Short
    exit("Long Ex", "Long", stop = avg x 0.98 (in a long signal), limit = avg x 10, when = bars since the long signal > 0);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are sent on every bar the condition holds (repeats ignored, pyramiding 1), so after a
      stop the next such bar re-enters. The exits are sent from the bar after the signal bar; the house
      bracket starts on the fill bar. The stop is 2 % and the target 900 % of the fill (scalar fractions,
      as written). The breakout factor 3.1 is never used. REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). Stops on 3-hour bars: mark coarse_bar_stop. The 100 % of equity size is sizing.
      FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, volume-flow balance with a rate-of-change filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the bull / bear volume SMAs; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426845_bull_bear_volume_flow_roc_filter_pct_stop_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [6, 12],
    "sl": [0.02, 0.04],
}
DEFAULT_PARAMS = {"length": 6, "sl": 0.02, "tp": 9.0, "roclength": 12, "pcnt_change": 2.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    bullma = v.where(c > o, 0.0).rolling(n).mean()
    bearma = v.where(o > c, 0.0).rolling(n).mean()
    k = int(p["roclength"])
    roc = 100 * (c - c.shift(k)) / c.shift(k)
    emaroc = roc.ewm(span=k // 2, adjust=False).mean()
    half = float(p["pcnt_change"]) / 2
    moving = (emaroc > half) | (emaroc < -half)
    le = (bullma > bearma) & moving
    se = (bullma < bearma) & moving
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
