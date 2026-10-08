"""MA Bollinger + RSI (always in): a bar opening below the lower 200-bar band and closing above it,
with RSI(6) having crossed above 50 within the last 11 bars, goes long; the mirror at the upper
band goes short.
Port of FMZ strategy #426557 "RSI Moving Average Bollinger Bands RSI Combo Strategy".

Source
    https://www.fmz.com/strategy/426557 (PineScript v4, FMZ last modified 2023-09-13 11:57:39).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 115-183), RSI 6 / 50, MA SMA 200, BB 200 x 2
    BBbull = open < lower and close > lower;  BBbear = open > upper and close < upper
    RSIbull = crossover(rsi(close, 6), 50) on this bar or any of the 10 before (RSIbear mirrors)
    BBbull and RSIbull -> entry long;  BBbear and RSIbear -> entry short
    strategy.close(id = "Long exit") / strategy.close(id = "Short Exit")

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the two strategy.close calls name ids that no entry uses ("Long exit" /
      "Short Exit" vs "Long entry" / "Short entry"), so they close nothing: a position ends only
      at the opposite entry. The saved 6 % stop levels only plot.
    * stdev is Pine's population deviation. MA type SMA (source default).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426557_ma_bollinger_rsi"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [6, 14],
    "bb_len": [100, 200],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"rsi_len": 6, "rsi_mid": 50, "bb_len": 200, "bb_mult": 2.0, "lookback": 11}


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["bb_len"])
    ma = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    upper, lower = ma + dev, ma - dev
    rsi = _rsi_pine(c, int(p["rsi_len"]))
    r1 = rsi.shift(1)
    bull = ((rsi > p["rsi_mid"]) & (r1 <= p["rsi_mid"])).astype(float)
    bear = ((rsi < p["rsi_mid"]) & (r1 >= p["rsi_mid"])).astype(float)
    k = int(p["lookback"])
    recent_bull = bull.rolling(k, min_periods=1).max() > 0
    recent_bear = bear.rolling(k, min_periods=1).max() > 0
    long_ = ((o < lower) & (c > lower) & recent_bull).to_numpy()
    short = ((o > upper) & (c < upper) & recent_bear).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
