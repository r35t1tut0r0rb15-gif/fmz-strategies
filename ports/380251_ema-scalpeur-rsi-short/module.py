"""EMA scalpeur (short side, Zer3192): EMA 9 crossing below EMA 26 with RSI(5) above 40 goes short;
EMA 100 crossing above EMA 55 closes the short. Short only.
Port of FMZ strategy #380251 "EMA SCALPEUR".

Source
    https://www.fmz.com/strategy/380251 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-27 17:17:28). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-89), EMA 9 / 26 / 100 / 55, RSI 5
    sell = crossunder(ema9, ema26) and rsi(5) > 40 -> entry short
    sellexit = crossover(ema100, ema55) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Short only, as written (rule 6: no split versions). Opposite entries cannot occur;
      portfolio_kwargs returns upon_opposite_entry="ignore".
    * A close on the bar of a new entry does not apply (the entry is not open yet); an entry
      while short is ignored.
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380251_ema_cross_short_only"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_l": [9, 12],
    "ema_l2": [21, 26],
    "rsi_len": [5, 14],
}
DEFAULT_PARAMS = {"ema_l": 9, "ema_l2": 26, "ema_s": 100, "ema_s2": 55, "rsi_len": 5}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    e1, e2, e3, e4 = e(p["ema_l"]), e(p["ema_l2"]), e(p["ema_s"]), e(p["ema_s2"])
    rsi = _rsi(c, int(p["rsi_len"]))
    sell = ((e1 < e2) & (e1.shift(1) >= e2.shift(1)) & (rsi > 40)).to_numpy()
    out = ((e3 > e4) & (e3.shift(1) <= e4.shift(1))).to_numpy()
    m = len(c)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and sell[i]:
            se[i], pos = True, -1
        elif pos == -1 and out[i]:
            sx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return false.copy(), false.copy(), pd.Series(se, index=idx), pd.Series(sx, index=idx)


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
