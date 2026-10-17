"""Fourier-shifted EMAs, 1-minute bars: the close plus the amplitude of the 1st, 2nd and 3rd harmonic of its last 64 bars
is smoothed by EMA 200, 20 and 5; the fast line above the middle one with the close above the slow line goes long, the
mirror goes short, held otherwise and reversed on the opposite condition.
Port of FMZ strategy #434326 "Low Frequency Fourier Transform Trend Following Moving Average Strategy" (FTSMA).

FMZ source id: 434326

Source
    https://www.fmz.com/strategy/434326 (PineScript v4, FMZ last modified 2023-12-05 14:56:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 156-309), source close; slow / mid / fast EMA 200 / 20 / 5 on sinusoids 1 / 2 / 3; lookback N 64; MA type EMA; linreg off; TP / SL / trail 0 (off)
    sx(0, k) = ReX_(k) = 2 / N x sum_{i=0..N-1} close[i] cos(2 pi k i / N)
    SLOW = ema(close + sx(0, 1), 200);  MED = ema(close + sx(0, 2), 20);  FAST = ema(close + sx(0, 3), 5)
    FAST > MED and close > SLOW -> entry long;  FAST < MED and close < SLOW -> entry short;  exits with TP / SL / trail 0 (na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * At i = 0 the sine terms vanish, so each shift is the cosine amplitude 2 ReX(k) / N of the last N
      closes (k 1 to 3 are neither 0 nor N / 2). The author's series approximation of pi (20 terms of
      the arctan 1/2 + arctan 1/3 formula) equals pi to double precision: np.pi.
    * The EMA type is the default; the other MA types and the linear regression are off. All
      risk inputs are 0, so the exits are never armed: dropped. strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed price with harmonic shifts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434326 (2 members, best partner #365882, Jaccard 0.965); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434326_fourier_shifted_ema"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_fourier": [64, 32],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"n_fourier": 64, "slow": 200, "mid": 20, "fast": 5, "sin1": 1, "sin2": 2, "sin3": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _amp(v, n, k):
    """2 / n x sum_{i=0..n-1} v[t - i] cos(2 pi k i / n) at every bar t (NaN before n bars)."""
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        i = n - 1 - np.arange(n)          # window position j holds v[t - (n - 1 - j)]
        w = np.cos(2 * np.pi * k * i / n)
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    scale = 1.0 / n if (k == 0 or 2 * k == n) else 2.0 / n
    return out * scale


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    n = int(p["n_fourier"])
    sh = lambda k: pd.Series(cv + _amp(cv, n, int(k)), index=c.index)  # noqa: E731
    slow = sh(p["sin1"]).ewm(span=int(p["slow"]), adjust=False).mean()
    med = sh(p["sin2"]).ewm(span=int(p["mid"]), adjust=False).mean()
    fast = sh(p["sin3"]).ewm(span=int(p["fast"]), adjust=False).mean()
    lc = ((fast > med) & (c > slow)).to_numpy()
    sc = ((fast < med) & (c < slow)).to_numpy()
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        if sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
