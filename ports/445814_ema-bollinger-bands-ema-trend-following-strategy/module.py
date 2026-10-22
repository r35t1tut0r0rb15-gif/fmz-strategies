"""Upper-band breakouts above the EMA 100, 1-hour bars: a close above both the EMA 100 and the upper band (50, 2) goes long; the close crossing under the lower band or under the EMA goes short; reversing.
Port of FMZ strategy #445814 "布林带EMA趋势跟踪策略Bollinger-Bands-EMA-Trend-Following-Strategy" (Bollinger Bands + EMA Strategy).

FMZ source id: 445814

Source
    https://www.fmz.com/strategy/445814 (PineScript v4, FMZ last modified 2024-03-22 14:27:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-192), BB 50 / 2; EMA 100; ATR 14 x 1.8 (plot only)
    close > ema100 and close > upper -> entry Buy;  crossunder(close, lower) or crossunder(close, ema100) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long condition is a level, so a repeated entry while long is ignored. The ATR only plots.
      Pine's stdev is the population deviation. No exit: positions end at the opposite entry.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakout above an EMA, band / EMA breakdowns.
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

NAME = "fmz_445814_upper_band_above_ema100_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [50, 20],
    "ema_len": [100, 200],
}
DEFAULT_PARAMS = {"bb_len": 50, "ema_len": 100, "width": 2.0}


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
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["width"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    c1 = c.shift(1)
    le = (c > e) & (c > upper)
    se = ((c < lower) & (c1 >= lower.shift(1))) | ((c < e) & (c1 >= e.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
