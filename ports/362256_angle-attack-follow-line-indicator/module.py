"""Follow Line flips: a Bollinger-break trend line (low - ATR in up-breaks, high + ATR in
down-breaks, ratcheting) changing direction; long on a flip up, short on a flip down.
Port of FMZ strategy #362256 "Angle-Attack-Follow-Line-Indicator".

Source
    https://www.fmz.com/strategy/362256 (PineScript v5, FMZ last modified 2022-05-10 21:29:29).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 156-449), BB 21 x 1, ATR 5, ATR filter on,
mode "NO FILTER HIGHER TIME FRAME"
    BBSignal = close > upperBB ? 1 : close < lowerBB ? -1 : 0
    up:   TrendLine = low - atr(5), never below its previous value
    down: TrendLine = high + atr(5), never above its previous value; 0: unchanged
    iTrend = +1 when TrendLine rises, -1 when it falls, else unchanged
    iTrend flips -1 -> +1 -> entry long;  +1 -> -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default mode does not use the 240-minute follow line, the angle "add"/"reduce" signals
      or the higher-timeframe filter; only buy_0/sell_0 send orders.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362256_follow_line_flip"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_period": [14, 21, 34],
    "bb_dev": [1.0, 1.5],
    "atr_period": [5, 10],
}
DEFAULT_PARAMS = {"bb_period": 21, "bb_dev": 1.0, "atr_period": 5}


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
    c = bars_df["close"]
    n = int(p["bb_period"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    sig = np.where(c > mid + sd * p["bb_dev"], 1, np.where(c < mid - sd * p["bb_dev"], -1, 0))
    atr = _atr_pine(bars_df, int(p["atr_period"])).to_numpy()
    h, lo = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(sig)
    tl = np.full(m, np.nan)
    trend = np.full(m, np.nan)
    for i in range(m):
        prev = tl[i - 1] if i else np.nan
        if sig[i] == 1:
            v = lo[i] - atr[i]
            tl[i] = prev if v < prev else v
        elif sig[i] == -1:
            v = h[i] + atr[i]
            tl[i] = prev if v > prev else v
        else:
            tl[i] = prev
        t = trend[i - 1] if i else np.nan
        if tl[i] > prev:
            t = 1
        elif tl[i] < prev:
            t = -1
        trend[i] = t
    t1 = np.roll(trend, 1)
    t1[0] = np.nan
    return _always_in((t1 < 0) & (trend > 0), (t1 > 0) & (trend < 0), bars_df.index)


def portfolio_kwargs(**params):
    return {}
