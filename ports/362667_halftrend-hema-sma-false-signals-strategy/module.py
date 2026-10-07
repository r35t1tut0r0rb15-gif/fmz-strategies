"""HalfTrend flip confirmed by the Hull estimate (HEMA) against a 150 SMA and a candle body clear
of the HEMA: an up-flip with HEMA > SMA and the body above HEMA goes long; the mirror goes short.
Port of FMZ strategy #362667 "HALFTREND + HEMA + SMA (FALSE SIGNAL)".

Source
    https://www.fmz.com/strategy/362667 (PineScript v5, FMZ last modified 2022-05-12 17:53:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 103-238), SMA 150, HEMA 50, amplitude 1
    hema = 3 * wma(close, length / 2) - 2 * ema(close, length / 2);  sma = sma(close, 150)
    HalfTrend (amplitude 1, ATR 100): buySignal = trend flips 1 -> 0, sellSignal = 0 -> 1
    long  = hema > sma and buySignal and min(open, close) > hema and max(open, close) > hema
    short = hema < sma and sellSignal and min(open, close) < hema and max(open, close) < hema
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highPrice = high[|highestbars(amplitude)|] is the rolling high of `amplitude` bars (lowPrice
      mirrors). The arrow (and so the signal) needs ATR(100), so nothing fires before bar 100.
    * "Full candle outside the HEMA" defaults to false (body test); the SMA plot offset (6) is
      display only. HEMA length is kept even (length / 2 exact).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362667_halftrend_hema_sma"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [100, 150, 200],
    "hema_len": [40, 50, 60],
}
DEFAULT_PARAMS = {"sma_len": 150, "hema_len": 50, "amplitude": 1}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _halftrend(bars, amplitude, atr_len=100):
    """HalfTrend (everget): returns (trend, buy, sell); trend 0 = up, 1 = down.

    buy = trend flips 1 -> 0 on a bar where ATR(atr_len) exists (arrowUp not na); sell mirrors.
    """
    h, l, c = bars["high"].to_numpy(float), bars["low"].to_numpy(float), bars["close"].to_numpy(float)
    hp = bars["high"].rolling(amplitude).max().to_numpy()
    lp = bars["low"].rolling(amplitude).min().to_numpy()
    hma = bars["high"].rolling(amplitude).mean().to_numpy()
    lma = bars["low"].rolling(amplitude).mean().to_numpy()
    atr_ok = _atr_pine(bars, atr_len).notna().to_numpy()
    m = len(c)
    trend_a = np.zeros(m, dtype=int)
    buy, sell = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    trend = next_trend = 0
    max_low = l[0] if m else np.nan
    min_high = h[0] if m else np.nan
    for i in range(m):
        pl = l[i - 1] if i else l[i]
        ph = h[i - 1] if i else h[i]
        if next_trend == 1:
            max_low = max(lp[i], max_low) if not np.isnan(lp[i]) else np.nan
            if hma[i] < max_low and c[i] < pl:
                trend, next_trend, min_high = 1, 0, hp[i]
        else:
            min_high = min(hp[i], min_high) if not np.isnan(hp[i]) else np.nan
            if lma[i] > min_high and c[i] > ph:
                trend, next_trend, max_low = 0, 1, lp[i]
        trend_a[i] = trend
        if i and trend != trend_a[i - 1] and atr_ok[i]:
            buy[i], sell[i] = trend == 0, trend == 1
    return trend_a, buy, sell


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
    c, o = bars_df["close"], bars_df["open"]
    half = int(p["hema_len"]) // 2
    hema = 3 * _wma(c, half) - 2 * c.ewm(span=half, adjust=False).mean()
    sma = c.rolling(int(p["sma_len"])).mean()
    _, buy, sell = _halftrend(bars_df, int(p["amplitude"]))
    lo, hi = np.minimum(o, c), np.maximum(o, c)
    long_ = ((hema > sma) & (lo > hema) & (hi > hema)).to_numpy() & buy
    short = ((hema < sma) & (lo < hema) & (hi < hema)).to_numpy() & sell
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
