"""SuperTrend (ATR 10 x 3) taken against its direction, hourly bars: after each direction change the position is long while the SuperTrend points down and short while it points up; reversing.
Port of FMZ strategy #477519 "Enhanced Trend Multi Signal Dynamic Trading Strategy" (Supertrend Strategy).

FMZ source id: 477519

Source
    https://www.fmz.com/strategy/477519 (PineScript v5, FMZ last modified 2025-01-06 11:06:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-142), SuperTrend ATR 10 x 3; custom 3-candle signals 15-19 bars after the last opposite bar
    dir changes -> direction := dir > 0 ? 1 : -1;  direction == -1 -> entry Short (every bar);  direction == 1 -> entry Long (every bar)
    15-19 bars after the last direction -1 bar and three green candles -> entry "Bullish Upward Signal" long;  mirror -> entry "Bearish Downward Signal" short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's direction is -1 in an up-trend, so direction -1 (an up-trend) enters SHORT and 1 enters
      LONG: the script trades against the SuperTrend, as written. The entries repeat every bar and are
      ignored while that side is held. The custom signals need 15-19 bars since the last bar of the other
      direction, so they come only while that same side is already held and never change the position.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, contrarian SuperTrend direction.
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

NAME = "fmz_477519_supertrend10x3_contrarian_direction_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_period": 10}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[1].to_numpy()
    m = len(d)
    state = np.zeros(m)
    cur = 0.0
    for i in range(1, m):
        if not np.isnan(d[i - 1]) and d[i - 1] != d[i]:
            cur = 1.0 if d[i] > 0 else -1.0
        state[i] = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(state == 1, index=ix), false, pd.Series(state == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
