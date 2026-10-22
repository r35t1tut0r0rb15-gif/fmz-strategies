"""MACD histogram zero crossings, 1-hour bars: crossing up goes long with a take-profit just above the signal bar's high, crossing down goes short (no exit for the short); reversing.
Port of FMZ strategy #448070 "MACD-Valley-Detector-策略-MACD-Valley-Detector-Strategy" (MACD Valley Detector).

FMZ source id: 448070

Source
    https://www.fmz.com/strategy/448070 (PineScript v5, FMZ last modified 2024-04-12 17:01:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-159), MACD 12 / 26 / 9 (delta = macd - signal); take profit high + 0.3; qty 1
    crossover(delta, 0) -> entry MacdLE (qty 1), exit(MacdLE, limit = high + 0.3);  crossunder(delta, 0) -> entry MacdSE, exit("exit long", MacdLE, limit = low - 0.3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long's target is the signal bar's high plus 0.3 price units (criterion 2: 0.3 against BTC
      near 42000 is 0.0000071 of the price): tp_stop = (high - close) / close + 0.0000071, shifted one
      bar inside stops() and re-based on the fill, on long entries only. The short's exit call names
      the long's id, so the short has no exit and ends at the next long entry; the exit it re-sends for
      the long only meets a long that is being reversed. The valley block only raises alerts.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The qty 1 is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long target fixed on the signal bar.
    2 generic: PASS, MACD histogram zero crossings with a long target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty 1 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_448070_macd_hist_zero_cross_long_high_target_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "offset_frac": 0.0000071}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (delta > 0) & (delta.shift(1) <= 0)
    se = (delta < 0) & (delta.shift(1) >= 0)
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _ = _signals(bars_df, p)
    c = bars_df["close"]
    tp = ((bars_df["high"] - c) / c + float(p["offset_frac"])).where(le)
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
