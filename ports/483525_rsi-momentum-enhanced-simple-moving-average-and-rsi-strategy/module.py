"""SMA 8 / 21 crossings with RSI 14 under 70 / over 30, 6-minute bars: the up-cross goes long, the down-cross closes the long and goes short, each with a 1 % stop and a 2 % target from the fill; reversing.
Port of FMZ strategy #483525 "基于动量增强型简单移动平均线和RSI的趋势跟踪策略-Momentum-Enhanced-Simple-Moving-Average-and-RSI-Strategy-for-Trend-Following" (WEN - SMA with RSI Strategy).

FMZ source id: 483525

Source
    https://www.fmz.com/strategy/483525 (PineScript v6, FMZ last modified 2025-02-24 10:19:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-152), SMA 8 / 21; RSI 14 / 70 / 30; stop 1 %; target 2 %
    crossover(sma8, sma21) and rsi < 70 -> entry Long;  crossunder and rsi > 30 -> close Long, entry Short
    every bar: exit Long (stop = avg x 0.99, limit = avg x 1.02);  exit Short (stop = avg x 1.01, limit = avg x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent every bar around the average price, which is na while flat and constant while
      held; they are ported as fixed fractions of the fill, active from the fill bar (as #440797). An
      entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4).
      No sizing code. FREQ = "6min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, SMA crossings with RSI filters.
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

NAME = "fmz_483525_sma8_21_cross_rsi_filter_1_2pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "6min"  # backtest header period: 6m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_length": [8, 5],
    "long_length": [21, 50],
}
DEFAULT_PARAMS = {"short_length": 8, "long_length": 21, "rsi_length": 14, "stop_loss": 1.0, "take_profit": 2.0}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["short_length"])).mean(), c.rolling(int(p["long_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 30)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["take_profit"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
