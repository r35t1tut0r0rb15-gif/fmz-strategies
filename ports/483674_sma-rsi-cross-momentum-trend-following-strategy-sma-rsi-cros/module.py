"""Close crossing SMA 20 with RSI 8 momentum, long only, 1-hour bars: the close crossing above SMA 20 with RSI(8)
above 60 goes long; the close crossing below SMA 20 with RSI(8) below 40 closes it.
Port of FMZ strategy #483674 "交叉动能趋势跟踪策略SMA-RSI交叉动量系统-Cross-Momentum-Trend-Following-Strategy-SMA-RSI-Cross-Momentum-System" (STOCKS TO BUY).

FMZ source id: 483674

Source
    https://www.fmz.com/strategy/483674 (PineScript v5, FMZ last modified 2025-02-25 10:44:04).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-205), SMA 20, RSI 8
    buy = crossover(close, sma20) and rsi > 60 -> entry long
    sell = crossunder(close, sma20) and rsi < 40 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The success / failure counters (2 % rise, low below the signal low within 7 bars) only feed the table: not
      ported. fill_orders_on_standard_ohlc has no effect on ordinary candles.
    * Long only; the source has no shorts. Exit signals are ignored while flat. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving average and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483674_sma20_cross_rsi8_long"
FAMILY = "momentum"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_buy": [60, 55],
    "rsi_sell": [40, 45],
}
DEFAULT_PARAMS = {"sma_len": 20, "rsi_len": 8, "rsi_buy": 60, "rsi_sell": 40}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((c > sma) & (c.shift(1) <= sma.shift(1)) & (rsi > p["rsi_buy"])).astype(bool)
    long_x = ((c < sma) & (c.shift(1) >= sma.shift(1)) & (rsi < p["rsi_sell"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
