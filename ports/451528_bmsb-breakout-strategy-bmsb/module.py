"""Bull-market support band crossings, 1-hour bars: the close crossing over the SMA 20 goes long and crossing under the EMA 21 goes short, each after closing what is open; reversing.
Port of FMZ strategy #451528 "BMSB-Breakout-Strategy-BMSB-突破策略" (BMSB Breakout Strategy).

FMZ source id: 451528

Source
    https://www.fmz.com/strategy/451528 (PineScript v5, FMZ last modified 2024-05-15 16:40:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-147), SMA 20; EMA 21 (security on the chart's own period)
    crossover(close, sma20) -> close_all if a trade is open, entry Buy;  crossunder(close, ema21) -> close_all if a trade is open, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security on the chart's own period returns the chart's own SMA / EMA. Each close_all is
      followed by the entry on the same bar: a reversal, or a close and re-entry on the held side that
      leaves the position on. When both crossings fall on one bar the later Sell call wins (as
      #437773). Different rules from #451393 (band max / min there). REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, support-band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_451528_bmsb_sma20_ema21_cross_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [20, 50],
    "ema_len": [21, 50],
}
DEFAULT_PARAMS = {"sma_len": 20, "ema_len": 21}


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
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    c1 = c.shift(1)
    buy = (c > sma) & (c1 <= sma.shift(1))
    sell = (c < ema) & (c1 >= ema.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return buy & ~sell, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
