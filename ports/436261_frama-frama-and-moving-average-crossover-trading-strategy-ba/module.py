"""SMA 13 / 26 upcrossing above a fractal adaptive average, 30-minute bars, long only: the SMA 13 crossing over the SMA 26 with the FRAMA of hl2 under the close buys; the SMA 26 crossing over the
SMA 13, or the FRAMA crossing under the close, closes it. The FRAMA starts from zero, as written.
Port of FMZ strategy #436261 "基于双均线和FRAMA指标的多空交叉交易策略FRAMA-and-Moving-Average-Crossover-Trading-Strategy-Based-on-Dual-Moving-Average" (Fractal Adaptive Moving Average).

FMZ source id: 436261

Source
    https://www.fmz.com/strategy/436261 (PineScript v2, FMZ last modified 2023-12-22 16:08:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 127-161), SMA 13 / 26; FRAMA length 16, fast 1, slow 198
    dimen = (log(N1 + N2) - log(N3)) / log(2) with N1, N2, N3 the range per bar over the half windows and the full window;  alpha from exp(w (dimen - 1)) clamped, out = (1 - alpha) nz(out[1]) + alpha hl2
    entry: crossover(sma13, sma26) and out < close;  exit: crossover(sma26, sma13) or crossunder(out, close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * dimen takes the previous raw dimension (nz(dimen1[1])) when a range is zero, as written. The
      filter starts from zero, so its early values sit far under the price. Long only. FREQ = "30min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal adaptive average and an average cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG436261 (2 members, best partner #438806, Jaccard 0.955); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436261_frama_filtered_sma_cross_long"
FAMILY = "adaptive_average"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [16, 20],
    "sc": [198, 100],
}
DEFAULT_PARAMS = {"len": 16, "fc": 1, "sc": 198, "fast_ma": 13, "slow_ma": 26}


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


def _frama(h, lo, price, length, fc, sc):
    len1 = int(length / 2)
    w = np.log(2 / (sc + 1))
    h1, l1 = h.rolling(len1).max(), lo.rolling(len1).min()
    n1 = (h1 - l1) / len1
    h2, l2 = h.rolling(length).max().shift(len1), lo.rolling(length).min().shift(len1)
    n2 = (h2 - l2) / len1
    h3, l3 = h.rolling(length).max(), lo.rolling(length).min()
    n3 = (h3 - l3) / length
    with np.errstate(invalid="ignore", divide="ignore"):
        dimen1 = ((np.log(n1 + n2) - np.log(n3)) / np.log(2)).to_numpy()
    ok = ((n1 > 0) & (n2 > 0) & (n3 > 0)).to_numpy()
    x = price.to_numpy(dtype=float)
    m = len(x)
    out = np.zeros(m)
    for i in range(m):
        d1_prev = dimen1[i - 1] if i > 0 and not np.isnan(dimen1[i - 1]) else 0.0
        dimen = dimen1[i] if ok[i] else d1_prev
        if np.isnan(dimen):
            dimen = 0.0
        alpha1 = np.exp(w * (dimen - 1))
        old_alpha = 1.0 if alpha1 > 1 else (0.01 if alpha1 < 0.01 else alpha1)
        old_n = (2 - old_alpha) / old_alpha
        n_ = ((sc - fc) * (old_n - 1)) / (sc - 1) + fc
        a_ = 2 / (n_ + 1)
        alpha = 2 / (sc + 1) if a_ < 2 / (sc + 1) else (1.0 if a_ > 1 else a_)
        prev = out[i - 1] if i > 0 else 0.0
        out[i] = (1 - alpha) * prev + alpha * (0.0 if np.isnan(x[i]) else x[i])
    return pd.Series(out, index=price.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f, s = c.rolling(int(p["fast_ma"])).mean(), c.rolling(int(p["slow_ma"])).mean()
    out = _frama(h, lo, (h + lo) / 2, int(p["len"]), float(p["fc"]), float(p["sc"]))
    le = ((f > s) & (f.shift(1) <= s.shift(1)) & (out < c)).fillna(False)
    lx = (((s > f) & (s.shift(1) <= f.shift(1))) | ((out < c) & (out.shift(1) >= c.shift(1)))).fillna(False)
    false = pd.Series(False, index=bars_df.index)
    return (le & ~lx).astype(bool), lx.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
