"""MACD ReLoaded (VAR averages): MACD built from CMO-adaptive VAR averages (12 / 26) minus its own
VAR(9) trigger; the histogram crossing above zero goes long, below zero goes short.
Port of FMZ strategy #365283 "MACD ReLoaded".

Source
    https://www.fmz.com/strategy/365283 (PineScript v4, FMZ last modified 2022-05-24 10:15:32).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 80-378), MA type "VAR", lengths 12 / 26, trigger 9
    VAR(x, n) := nz(a |CMO9| x) + (1 - a |CMO9|) nz(VAR[1]),  a = 2 / (n + 1)
    src2 = VAR(close, 12) - VAR(close, 26);  hist = src2 - VAR(src2, 9)
    crossover(hist, 0) -> entry long;  crossunder(hist, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Moving-average type default "VAR" (the input() default; the argument table shows the
      option index). Zero crossings of MA differences are scale-free.
    * The date window (window() returns true) is unused; bar colouring only draws.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365283_macd_var_reloaded"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [21, 26],
    "trigger": [5, 9],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "trigger": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _var_ma(src, length):
    """VAR (Tushar Chande VIDYA as coded by KivancOzbilgic): EMA whose alpha is scaled by
    |CMO(9)|; nz() seeds: na inputs add 0 and the recursion starts from 0."""
    s = np.asarray(src, dtype=float)
    a = 2 / (length + 1)
    prev_s = np.concatenate([[np.nan], s[:-1]])
    ud = np.where(s > prev_s, s - prev_s, 0.0)
    dd = np.where(s < prev_s, prev_s - s, 0.0)
    sud = pd.Series(ud).rolling(9).sum().to_numpy()
    sdd = pd.Series(dd).rolling(9).sum().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        cmo = np.nan_to_num((sud - sdd) / (sud + sdd), nan=0.0, posinf=0.0, neginf=0.0)
    out = np.zeros(len(s))
    for i in range(len(s)):
        k = a * abs(cmo[i])
        term = k * s[i]
        out[i] = (0.0 if np.isnan(term) else term) + (1 - k) * (out[i - 1] if i else 0.0)
    return out


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
    c = bars_df["close"].to_numpy(dtype=float)
    src2 = _var_ma(c, int(p["fast"])) - _var_ma(c, int(p["slow"]))
    hist = src2 - _var_ma(src2, int(p["trigger"]))
    h1 = np.concatenate([[np.nan], hist[:-1]])
    return _always_in((hist > 0) & (h1 <= 0), (hist < 0) & (h1 >= 0), bars_df.index)


def portfolio_kwargs(**params):
    return {}
