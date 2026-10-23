"""Hourly bars, long only: a MACD crossing over its SMA 9 signal or a bullish engulfing candle, with RSI 14 under 70 and more up-candle than down-candle volume since the data start, goes long; the long closes on a MACD crossing under its signal or an RSI over 60.
Port of FMZ strategy #474952 "基于RSIMACD和成交量的多指标组合自适应交易策略-Multi-Indicator-Adaptive-Trading-Strategy-Based-on-RSI-MACD-and-Volume" (Liraz sh Strategy - RSI MACD Strategy with Bullish Engulfing and Net Volume).

FMZ source id: 474952

Source
    https://www.fmz.com/strategy/474952 (PineScript v5, FMZ last modified 2024-12-13 10:19:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 100-190), RSI 14 (rma); MACD 12 / 26 with an SMA 9 signal; engulfing; cumulative up - down volume
    upVolume += volume on up candles, downVolume += volume on down candles (var, never reset);  delta = upVolume - downVolume
    longCondition = (crossover(macd, signalLine) or bullishEngulfingSignal) and rsi < 70 and delta > 0 -> entry Long
    exitCondition = crossunder(macd, signalLine) or (rsi > 60 and position_size > 0) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The up / down volume totals are var sums that never reset, so delta is the net candle volume since
      the first bar of the data and depends on where the data starts (weird case). The MACD signal line is
      an SMA 9, as written. The close tests the position held at the bar's close, so it acts from the bar
      after the fill (an entry from flat on a crossing-under bar is kept); a signal while long adds
      nothing. The date window spans all data. The RSI MA only plots. Long only. Capital, commission and
      slippage are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings / engulfing candles filtered by RSI and net volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the cumulative up / down volume; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474952_macd_engulf_rsi_cum_net_volume_1h_long_only"
FAMILY = "macd"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_exit": [60.0, 70.0],
    "sig_len": [9, 14],
}
DEFAULT_PARAMS = {"rsi_exit": 60.0, "sig_len": 9}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    delta = v.where(c > o, 0.0).cumsum() - v.where(c < o, 0.0).cumsum()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.rolling(int(p["sig_len"])).mean()
    o1, c1 = o.shift(1), c.shift(1)
    engulf = (o1 > c1) & (c > o) & (c >= o1) & (c1 >= o) & ((c - o) > (o1 - c1))
    xo = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    xu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    buy = ((xo | engulf) & (r < 70) & (delta > 0)).to_numpy()
    hot = (r > float(p["rsi_exit"])).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0:
            if buy[i]:
                le[i], pos = True, 1
        elif xu[i] or hot[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
