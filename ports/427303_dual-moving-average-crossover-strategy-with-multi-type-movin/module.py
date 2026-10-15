"""Multi-X, long only: EMA 9 crossing above SMA 21 goes long, crossing back under closes the long
(the optional trend-zone filter MA 3 is off by default).
Port of FMZ strategy #427303 "Dual Moving Average Crossover Strategy with Multi-Type Moving Averages".

FMZ source id: 427303

Source
    https://www.fmz.com/strategy/427303 (PineScript v4, FMZ last modified 2023-09-19 21:27:31).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 175-266), MA 1 EMA 9, MA 2 SMA 21, MA 3 off (SMA 50 of highs / lows)
    crossover(ma1, ma2) -> entry long (with MA 3 on: only if close > MA 3 of highs; also on
    crossover(close, MA 3 of highs)); crossunder(ma1, ma2) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * `ma3_on` (the source's "MA No.3" switch, default off) is in the grid. The VWMA choice of the
      MA types uses volume and is not offered (check 8); SMA / EMA / RMA / WMA are.
    * inDateRange is the constant true: no window.
    * Long only; entries only from flat.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the VWMA type is excluded.
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427303_multi_x_ma_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_len": [9, 20],
    "ma2_len": [21, 50],
    "ma3_on": [False, True],
}
DEFAULT_PARAMS = {"ma1_type": "EMA", "ma1_len": 9, "ma2_type": "SMA", "ma2_len": 21,
                  "ma3_on": False, "ma3_type": "SMA", "ma3_len": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _ma(x, n, t):
    if t == "SMA":
        return x.rolling(n).mean()
    if t == "EMA":
        return x.ewm(span=n, adjust=False).mean()
    if t == "RMA":
        return _rma(x, n)
    if t == "WMA":
        w = np.arange(1, n + 1, dtype=float)
        return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)
    raise ValueError(f"MA type {t!r} not ported (VWMA uses volume)")


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    m1 = _ma(c, int(p["ma1_len"]), p["ma1_type"])
    m2 = _ma(c, int(p["ma2_len"]), p["ma2_type"])
    up = ((m1 > m2) & (m1.shift(1) <= m2.shift(1))).to_numpy()
    dn = ((m1 < m2) & (m1.shift(1) >= m2.shift(1))).to_numpy()
    if bool(p["ma3_on"]):
        m3h = _ma(bars_df["high"], int(p["ma3_len"]), p["ma3_type"])
        zone = ((c > m3h) & (c.shift(1) <= m3h.shift(1))).to_numpy()
        entry = (up & (c > m3h).to_numpy()) | zone
    else:
        entry = up
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and dn[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
