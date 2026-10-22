"""EMA 5 / 10 crossings with an RSI 14 filter, 1-hour bars: the cross up with the RSI under 70 goes long, the cross down with the RSI over 30 goes short; reversing.
Port of FMZ strategy #454740 "Multi Indicator High Frequency Trading Strategy Short Term Trading System Combining Exponential Moving Averages and Momentum Indicators" (Scalping EMA RSI MACD).

FMZ source id: 454740

Source
    https://www.fmz.com/strategy/454740 (PineScript v5, FMZ last modified 2024-06-21 15:23:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-228), EMA 5 / 10; RSI 14 (70 / 30); MACD and the divergence markers plotted only
    crossover(ema5, ema10) and rsi < 70 -> entry Compra;  crossunder and rsi > 30 -> entry Venta

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MACD and the 'divergence' tests are only plotted. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454740_ema5_10_cross_rsi_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 9],
    "slow": [10, 21],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 10, "rsi_len": 14}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
