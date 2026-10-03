"""Ichimoku double cross (close crosses Tenkan and Kijun on the same bar), direction set by
cloud thickness. Port of FMZ strategy #55839 "一目均衡" (Ichimoku).

Source
    https://www.fmz.com/strategy/55839 (JavaScript, author "icesun963", FMZ last modified
    2017-09-27 13:52:15). Verbatim copy: original_source.md. Read 2026-09-29.

Original signal (original_source.md lines 47-61, 81-90, 157-175, 213-230)
    TenkanSen  = (highest(High, 9)  + lowest(Low, 9))  / 2
    KijunSen   = (highest(High, 24) + lowest(Low, 24)) / 2
    SpanA = (Tenkan + Kijun)/2;  SpanB = (highest(High, 51) + lowest(Low, 51)) / 2
    absx = |SpanA - SpanB|   (current, not displaced)
    cross(X, close): close[t] > X[t] and X[t-1] > close[t-1], or close[t] < X[t] and X[t-1] < close[t-1]
    if cross(Tenkan) and cross(Kijun):
        absx < CX (thin cloud):  close < Tenkan -> buy,  else sell
        otherwise (thick cloud): close > Tenkan -> buy,  else sell
    Defaults: 9 / 24 / 51, CX 100 (price units). keh (Hull MA) and displacement only feed plots.

Interpretation choices
    * Evaluated on completed bars; the Donchian windows include the current bar
      (FMZ TA.Highest/TA.Lowest include the last record).
    * Criterion 2: CX = 100 is in price units. It becomes `cloud_atr` x ATR(atr_length):
      thin cloud when absx < cloud_atr * ATR[t].
    * Buy = go long, sell = go short. The original trades 1 unit per signal with no position
      tracking (units accumulate); that is sizing and is stored. REVERSAL INTENDED: entries only,
      portfolio_kwargs is {}, the engine's default opposite-entry reversal applies.
    * The Hull-MA colours (lines 127-152) and the displaced cloud / Chikou (lines 177-184) are
      computed but never used in a decision; not ported.
    * FREQ = "1h": the description says hourly bars and the loop sleeps one hour.
    * No costs here.
"""
import numpy as np
import pandas as pd

NAME = "fmz_55839_ichimoku_double_cross"
FAMILY = "ichimoku"  # proposed 2026-10-03, user to confirm
FREQ = "1h"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [6, 9, 12],
    "kijun": [18, 24, 36],
    "cloud_atr": [0.5, 1.0, 2.0],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 24, "span_b": 51, "cloud_atr": 1.0, "atr_length": 14}


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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _donchian_mid(bars, n):
    return (bars["high"].rolling(n).max() + bars["low"].rolling(n).min()) / 2.0


def _crosses(line, close):
    up = (close > line) & (line.shift(1) > close.shift(1))
    down = (close < line) & (line.shift(1) < close.shift(1))
    return up | down


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    tenkan = _donchian_mid(bars_df, int(p["tenkan"]))
    kijun = _donchian_mid(bars_df, int(p["kijun"]))
    span_a = (tenkan + kijun) / 2.0
    span_b = _donchian_mid(bars_df, int(p["span_b"]))
    thickness = (span_a - span_b).abs()
    atr = _atr(bars_df, int(p["atr_length"]))
    thin = thickness < p["cloud_atr"] * atr

    trigger = _crosses(tenkan, close) & _crosses(kijun, close) & thickness.notna() & atr.notna()
    buy = trigger & ((thin & (close < tenkan)) | (~thin & (close > tenkan)))
    sell = trigger & ~buy
    false = pd.Series(False, index=bars_df.index)
    return (buy.fillna(False).astype(bool), false.copy(),
            sell.fillna(False).astype(bool), false.copy())


def portfolio_kwargs(**params):
    return {}
