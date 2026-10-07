"""MACD line vs SMA signal line with a minimum gap: long when MACD is above the signal by more
than the gap, short when below by more than the gap (always in).
Port of FMZ strategy #361532 "MacD-Custom-Indicator-Multiple-Time-FrameAll-Available-Options"
(ChrisMoody CM_MacD_Ult_MTF with orders added).

Source
    https://www.fmz.com/strategy/361532 (PineScript, FMZ last modified 2022-05-06 21:35:07).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 72-110), 12 / 26 / 9
    outMacD = ema(close,12) - ema(close,26); outSignal = sma(outMacD, 9)
    outMacD > outSignal and abs(outMacD - outSignal) > 90 -> entry long
    else outMacD < outSignal and abs(...) > 90 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the gap of 90 price units (BTC) becomes `gap_atr` x Wilder ATR(14).
    * The multi-timeframe option is commented out in the source; the chart timeframe is used.
    * strategy.entry reverses an opposite position: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361532_macd_gap_side"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gap_atr": [0.1, 0.25, 0.5],
    "fast": [8, 12],
    "slow": [26, 34],
}
DEFAULT_PARAMS = {"gap_atr": 0.25, "fast": 12, "slow": 26, "signal": 9, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    diff = (macd - macd.rolling(int(p["signal"])).mean()).to_numpy()
    gap = p["gap_atr"] * _atr_pine(bars_df, int(p["atr_length"])).to_numpy()

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if diff[i] > 0 and abs(diff[i]) > gap[i]:
            if pos != 1:
                le[i], pos = True, 1
        elif diff[i] < 0 and abs(diff[i]) > gap[i] and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
