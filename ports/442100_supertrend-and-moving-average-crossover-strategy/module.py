"""EMA 10 / SMA 20 side with the SuperTrend direction value, 2-hour bars: the EMA 10 above the SMA 20 with ta.supertrend direction > 0 goes long, the EMA under the SMA with direction < 0 goes short;
reversing.
Port of FMZ strategy #442100 "Supertrend and Moving Average Crossover Strategy" (Supertrend and Moving Averages Strategy).

FMZ source id: 442100

Source
    https://www.fmz.com/strategy/442100 (PineScript v5, FMZ last modified 2024-02-19 11:56:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-184), SuperTrend factor 3, ATR 10; EMA 10, SMA 20
    [supertrend, direction] = ta.supertrend(3, 10);  ema10 > sma20 and direction > 0 -> entry Long;  ema10 < sma20 and direction < 0 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction is -1 in an uptrend and 1 in a downtrend, so as written the long needs
      the SuperTrend in its down state and the short its up state (ported as written). The conditions are
      levels; an entry while already in that direction does nothing. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "2h" from the backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA side and SuperTrend direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442100_ema10_sma20_side_supertrend_direction"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_length": [10, 14],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_length": 10, "factor": 3.0, "length_ema": 10, "length_sma": 20}


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


def _supertrend(h, lo, c, factor, n):
    """Pine's ta.supertrend(factor, atrPeriod): (line, direction), direction -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return st, d


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    _, d = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_length"]))
    dr = pd.Series(d, index=c.index)
    e = c.ewm(span=int(p["length_ema"]), adjust=False).mean()
    s = c.rolling(int(p["length_sma"])).mean()
    le = (e > s) & (dr > 0)
    se = (e < s) & (dr < 0)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
