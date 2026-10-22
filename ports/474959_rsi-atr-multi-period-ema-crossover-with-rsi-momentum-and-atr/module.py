"""Bullish engulfing candles in an EMA 100 / 200 uptrend with RSI over 50, 3-hour bars, long only: it buys with a 1.1 ATR stop and 2 ATR target from the fill price (the ATR of the bar before the fill; the source re-sends them with each bar's ATR, pending).
Port of FMZ strategy #474959 "多周期均线穿越结合RSI动量与ATR波动率的趋势跟踪策略-Multi-Period-EMA-Crossover-with-RSI-Momentum-and-ATR-Volatility-Based-Trend-Following-Strategy" (Bullish Engulfing with EMA Crossover and ATR-Based SL/TP with RSI Filter).

FMZ source id: 474959

Source
    https://www.fmz.com/strategy/474959 (PineScript v5, FMZ last modified 2024-12-13 10:33:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-146), EMA 100 / 200; RSI 14, 50; ATR 14: stop 1.1 x, target 2 x from avg
    close > open[1] and open < close[1] and close > open and ema100 > ema200 and rsi > 50 -> entry Buy;  long: exit(stop = avg - 1.1 atr, limit = avg + 2 atr) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent every bar from the fill price with the current ATR, so it moves with the
      ATR: ported with the ATR of the bar before the fill (as fractions of the fill), the moving part
      kept pending (mark trailing_stop_pending). Long only. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 3-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ATR bracket from the fill.
    2 generic: PASS, trend engulfing candles with an RSI filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474959_engulfing_ema100_200_rsi50_atr_bracket_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_ema": [100, 50],
    "long_ema": [200, 100],
}
DEFAULT_PARAMS = {"short_ema": 100, "long_ema": 200, "sl_atr": 1.1, "tp_atr": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    a = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    eng = (c > o.shift(1)) & (o < c.shift(1)) & (c > o)
    le = eng & (a > b) & (_rsi(c, 14) > 50)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    atr = _atr(bars_df, 14).shift(1)            # the ATR of the bar before the fill
    o = bars_df["open"]
    return {"sl_stop": float(p["sl_atr"]) * atr / o, "tp_stop": float(p["tp_atr"]) * atr / o}


def portfolio_kwargs(**params):
    return {}
