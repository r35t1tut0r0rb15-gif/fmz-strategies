"""SSL-hybrid continuation entries: long when the close is above the HMA(60) baseline and the
JMA SSL2 line, with that line within 0.9 x ATR(WMA) of the close; short mirror (always in).
Port of FMZ strategy #362210 "MA-HYBRID-BY-RAJ".

Source
    https://www.fmz.com/strategy/362210 (PineScript v4, FMZ last modified 2022-05-10 15:32:42).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 81-342), defaults: baseline HMA 60, SSL2 JMA 5
(phase 3, power 1), ATR 14 smoothed by WMA, continuation criterion 0.9
    sslDown2 = SSL switch of JMA(high,5)/JMA(low,5)
    buy_atr  = close - 0.9*atr < sslDown2 and close > BBMC and close > sslDown2
    sell_atr = close + 0.9*atr > sslDown2 and close < BBMC and close < sslDown2
    buy_atr -> entry long;  else sell_atr -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default MA types are ported (HMA baseline, JMA continuation); hma len/2 truncated.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362210_ssl_hybrid_continuation"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "baseline_len": [40, 60, 90],
    "ssl2_len": [5, 10],
    "atr_crit": [0.6, 0.9],
}
DEFAULT_PARAMS = {"baseline_len": 60, "ssl2_len": 5, "atr_crit": 0.9, "atr_len": 14,
                  "jma_phase": 3, "jma_power": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


def _jma_simple(src, length, phase, power):
    s = src.to_numpy(dtype=float)
    pr = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100 + 1.5)
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta ** power
    e0 = e1 = e2 = jma = 0.0
    out = np.full(len(s), np.nan)
    for t in range(len(s)):
        e0 = (1 - alpha) * s[t] + alpha * e0
        e1 = (s[t] - e0) * (1 - beta) + beta * e1
        e2 = (e0 + pr * e1 - jma) * (1 - alpha) ** 2 + alpha ** 2 * e2
        jma = out[t] = e2 + jma
    return pd.Series(out, index=src.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # tr(true)
    atr = _wma(tr, int(p["atr_len"])).to_numpy()
    bbmc = _hma(c, int(p["baseline_len"])).to_numpy()
    mh = _jma_simple(h, int(p["ssl2_len"]), p["jma_phase"], p["jma_power"]).to_numpy()
    ml = _jma_simple(lo, int(p["ssl2_len"]), p["jma_phase"], p["jma_power"]).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ssl2 = np.full(m, np.nan)
    hlv = np.nan
    for t in range(m):
        hlv = 1 if cv[t] > mh[t] else (-1 if cv[t] < ml[t] else hlv)
        ssl2[t] = mh[t] if hlv < 0 else ml[t]
    k = p["atr_crit"]
    buy = (cv - k * atr < ssl2) & (cv > bbmc) & (cv > ssl2)
    sell = (cv + k * atr > ssl2) & (cv < bbmc) & (cv < ssl2)
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
