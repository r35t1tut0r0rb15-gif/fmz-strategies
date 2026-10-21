"""RSI extremes with engulfing-style candles, 1-hour bars: an RSI 9 at or under 25 (now or on the previous bar) with a close above the previous open after a down candle goes long; an RSI at or over 60 with a close
under the previous open after an up candle goes short; reversing.
Port of FMZ strategy #437488 "基于RSI指标和包容涨跌形态的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-Indicator-and-Engulfing-Pattern" (RSI Swing Signals).

FMZ source id: 437488

Source
    https://www.fmz.com/strategy/437488 (PineScript v4, FMZ last modified 2024-01-03 11:24:08).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 140-172), RSI 9, overbought 60, oversold 25
    bullishEC = close > open[1] and close[1] < open[1];  bearishEC = close < open[1] and close[1] > open[1]
    long = (rsiOS or rsiOS[1]) and bullishEC -> entry Long;  short = (rsiOB or rsiOB[1]) and bearishEC -> entry Short;  exit(when = rsi crosses) with no price levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two strategy.exit calls give only `when` and no stop, limit or trail, so they place no order (as
      #429564); positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and candle comparisons.
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

NAME = "fmz_437488_rsi_extreme_engulfing"
FAMILY = "candle_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [9, 14],
    "oversold": [25.0, 30.0],
}
DEFAULT_PARAMS = {"rsi_len": 9, "oversold": 25.0, "overbought": 60.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    os_ = r <= float(p["oversold"])
    ob = r >= float(p["overbought"])
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c > o1) & (c1 < o1)
    bear = (c < o1) & (c1 > o1)
    lc = (os_ | os_.shift(1, fill_value=False)) & bull
    sc = (ob | ob.shift(1, fill_value=False)) & bear
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
