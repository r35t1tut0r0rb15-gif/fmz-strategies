"""T-Step LSMA (LuxAlgo, posted by Zer3192): a step line b that jumps to the (LSMA-smoothed)
price when it moves more than an adaptive threshold; b stepping up turns long, stepping down
turns short (always in).
Port of FMZ strategy #370711 "T-Step LSMA".

Source
    https://www.fmz.com/strategy/370711 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-25 16:26:42). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 35-60), length 100, sc 0.5
    src = 0.5 close + 0.5 nz(ls[1], close)
    er = 1 - |change(src, 100)| / sum(|change(src)|, 100)
    a = cum(|src - b[1]|) / bar_index * (1 + er)
    b := src beyond b[1] +- a ? src : b[1]
    alpha = fixnan(correlation(src, b, 100) * stdev(src, 100) / stdev(b, 100))
    ls = alpha b + sma(src, 100) - alpha sma(b, 100)
    osc = b up ? 1 : b down ? 0 : osc[1];  osc 0 -> 1 -> entry long; 1 -> 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cum() / bar_index is a running (expanding) mean from the first bar, as in Pine: causal, but
      it depends on where the data starts.
    * b holds still until er exists (100 bars), as coded (comparisons with na are false).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_370711_t_step_lsma"
FAMILY = "slope_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100, 200],
    "sc": [0.25, 0.5, 0.75],
}
DEFAULT_PARAMS = {"length": 100, "sc": 0.5}


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
    L, sc = int(p["length"]), float(p["sc"])
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    src, b, ls = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    cum_abs = 0.0
    alpha = np.nan
    for i in range(m):
        ls1 = ls[i - 1] if i else np.nan
        src[i] = sc * c[i] + (1 - sc) * (c[i] if np.isnan(ls1) else ls1)
        er = np.nan
        if i >= L:
            den = np.abs(np.diff(src[i - L:i + 1])).sum()
            with np.errstate(all="ignore"):
                er = 1 - abs(src[i] - src[i - L]) / den
        b1 = src[i] if (i == 0 or np.isnan(b[i - 1])) else b[i - 1]
        cum_abs += abs(src[i] - b1)
        a = cum_abs / i * (1 + er) if i else np.nan
        b[i] = src[i] if (src[i] > b1 + a or src[i] < b1 - a) else b1
        if i >= L - 1:
            x, y = src[i - L + 1:i + 1], b[i - L + 1:i + 1]
            vy = y.var()
            if vy > 0 and x.var() > 0:
                alpha = np.mean((x - x.mean()) * (y - y.mean())) / vy  # corr * sd(x) / sd(y)
            if not np.isnan(alpha):
                ls[i] = alpha * b[i] + x.mean() - alpha * y.mean()
    osc = np.full(m, np.nan)  # osc[1] is na on the first bar, so osc stays na until b first moves
    for i in range(1, m):
        osc[i] = 1.0 if b[i] > b[i - 1] else (0.0 if b[i] < b[i - 1] else osc[i - 1])
    d = osc - np.concatenate([[np.nan], osc[:-1]])  # change(osc); na never signals
    return _always_in(d > 0, d < 0, bars_df.index)


def portfolio_kwargs(**params):
    return {}
