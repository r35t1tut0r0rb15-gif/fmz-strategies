"""Close above / below one SMA, always in the market (stop-and-reverse demo).
Port of FMZ strategy #193609 "一根均线-趋势-Demo" (one moving average, trend demo).

Source
    https://www.fmz.com/strategy/193609 (JavaScript, author "扁豆子", FMZ last modified
    2020-04-11 21:28:30). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 41-81)
    MA = TA.MA(records, 30); once per new bar ("K线结束后进行交易"):
    idle:  Bar.Close > MA -> buy;  Bar.Close < MA -> sell short
    long:  Bar.Close < MA -> close long and sell short
    short: Bar.Close > MA -> close short and buy

Interpretation choices
    * The bot acts on the first poll of each new bar, reading records[-1] (the new, forming bar)
      and an MA that includes it; the port evaluates the same rule on completed bar t
      (records[-1] -> t, MA window ending at t).
    * Close and open-opposite in the same pass: REVERSAL INTENDED (portfolio_kwargs {}; the
      engine's default opposite-entry reversal applies). Always in after the first signal.
    * XBTUSD contract and Amount are venue/sizing (original_sizing.txt).
    * No bar size in the source (GetRecords() default, no backtest header):
      FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_193609_single_sma_reverse"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [10, 20, 30, 50, 100],
}
DEFAULT_PARAMS = {"ma_length": 30}


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
    ma = c.rolling(int(p["ma_length"])).mean()
    above, below = (c > ma).to_numpy(), (c < ma).to_numpy()

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if above[i] and pos != 1:
            le[i], pos = True, 1
        elif below[i] and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
