"""K's Reversal Indicator I: a candle at the outer Bollinger band followed by a MACD cross in
the reversal direction; stop-and-reverse.
Port of FMZ strategy #361785 "Ks-Reversal-Indicator-I" (Sofien Kaabar, orders added).

Source
    https://www.fmz.com/strategy/361785 (PineScript v5, FMZ last modified 2022-05-08 11:14:32).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 59-81), MACD 12/26/9, Bollinger 100 x 2
    buy  = min(open[1],close[1]) <= lower[1] and max(open[1],close[1]) <= mid
           and macd[1] > signal[1] and macd[2] < signal[2]
    sell = max(open[1],close[1]) >= upper[1] and min(open[1],close[1]) >= mid
           and macd[1] < signal[1] and macd[2] > signal[2]
    buy -> entry long;  else sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * `mid` is the current bar's band mid while the candle test uses the previous bar, as written.
    * ta.stdev is the population deviation.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361785_ks_band_macd_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100, 200],
    "multiplier": [1.5, 2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 100, "multiplier": 2.0, "fast": 12, "slow": 26, "signal": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    n = int(p["length"])
    mid = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    lower, upper = mid - p["multiplier"] * sd, mid + p["multiplier"] * sd
    lo1 = np.minimum(o.shift(1), c.shift(1))
    hi1 = np.maximum(o.shift(1), c.shift(1))
    buy = ((lo1 <= lower.shift(1)) & (hi1 <= mid) & (macd.shift(1) > sig.shift(1))
           & (macd.shift(2) < sig.shift(2))).to_numpy()
    sell = ((hi1 >= upper.shift(1)) & (lo1 >= mid) & (macd.shift(1) < sig.shift(1))
            & (macd.shift(2) > sig.shift(2))).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
