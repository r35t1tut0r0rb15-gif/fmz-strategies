"""Hull MA crossing its last local minimum (long) or last local maximum (short),
stop-and-reverse.
Port of FMZ strategy #362327 "Hull-4ema".

Source
    https://www.fmz.com/strategy/362327 (PineScript v4, FMZ last modified 2022-05-10 23:47:44).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-138), source hl2, HMA 21
    HMA = hma(hl2, 21)
    saveMA_Min = valuewhen(HMA > HMA[1] and HMA[1] < HMA[2], HMA[1], 0)
    saveMA_Max = valuewhen(HMA < HMA[1] and HMA[1] > HMA[2], HMA[1], 0)
    crossover(HMA, saveMA_Min) -> entry long;  else crossunder(HMA, saveMA_Max) -> entry short
    (the four EMAs and Bollinger bands of the name are plotted only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * hma(len) = wma(2*wma(src, len/2) - wma(src, len), round(sqrt(len))); len/2 truncated to int.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362327_hma_local_extreme_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hma_len": [14, 21, 34, 55],
}
DEFAULT_PARAMS = {"hma_len": 21}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hma = _hma((bars_df["high"] + bars_df["low"]) / 2, int(p["hma_len"]))
    h1, h2 = hma.shift(1), hma.shift(2)
    is_min = (hma > h1) & (h1 < h2)
    is_max = (hma < h1) & (h1 > h2)
    save_min = h1.where(is_min)
    save_max = h1.where(is_max)
    v_min, v_max = np.full(len(hma), np.nan), np.full(len(hma), np.nan)
    last_min = last_max = np.nan
    for i, (a, b) in enumerate(zip(save_min.to_numpy(), save_max.to_numpy())):   # valuewhen(..., 0)
        last_min = a if not np.isnan(a) else last_min
        last_max = b if not np.isnan(b) else last_max
        v_min[i], v_max[i] = last_min, last_max
    vmin, vmax = pd.Series(v_min, index=hma.index), pd.Series(v_max, index=hma.index)
    up = ((hma > vmin) & (hma.shift(1) <= vmin.shift(1))).to_numpy()
    dn = ((hma < vmax) & (hma.shift(1) >= vmax.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
