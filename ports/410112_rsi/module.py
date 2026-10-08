"""RSI oversold / overbought (spot, long only): RSI 14 below 30 buys when flat; RSI above 70 sells
the holding.
Port of FMZ strategy #410112 "分享RSI超买超卖策略".

Source
    https://www.fmz.com/strategy/410112 (Python, author 盯盘狗 - 策略出租, FMZ last modified
    2023-04-18 12:46:08). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 22-66), period 1m, RSI 14 (talib), 30 / 70
    rsi[-1] < 30 and not holding -> buy;  rsi[-1] > 70 and holding -> sell

Interpretation choices (MyLanguage / FMZ notes in SURVEY_README.md)
    * The loop polls every 60 s and reads klines[-1], the forming bar; the port evaluates on the
      completed bar (FMZ GetRecords convention, as #345289).
    * talib.RSI is Wilder's. Long only (spot), as written: opposite entries cannot occur;
      portfolio_kwargs returns upon_opposite_entry="ignore".
    * FREQ = "1min" from the code (period = '1m').

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_410112_rsi_30_70_long_only"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # code: period = '1m'
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [7, 14, 21],
    "rsi_buy": [25, 30],
    "rsi_sell": [70, 75],
}
DEFAULT_PARAMS = {"rsi_period": 14, "rsi_buy": 30, "rsi_sell": 70}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi(bars_df["close"], int(p["rsi_period"])).to_numpy()
    m = len(rsi)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    holding = False
    for i in range(m):
        if rsi[i] < p["rsi_buy"] and not holding:
            le[i], holding = True, True
        elif rsi[i] > p["rsi_sell"] and holding:
            lx[i], holding = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
