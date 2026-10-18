"""Three-average alignment with a self-powered Kaufman average, 1-hour bars: SMA 16 > 36 > 72 with the close over the trend SMA 100, a moving KAMA 50 and the close over it goes long; the mirror goes short; a
reverse alignment against the trend SMA (close_all) flattens.
Port of FMZ strategy #436491 "Three SMA Crossover Momentum Strategy" (Three SMA-crossover strategy [30min]).

FMZ source id: 436491

Source
    https://www.fmz.com/strategy/436491 (PineScript v5, FMZ last modified 2023-12-25 12:06:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 139-195), SMA 16 / 36 / 72, trend SMA 100, KAMA length 50, self powered
    long_cond = SMA1 > SMA2 > SMA3 and trend SMA < close and not a_f and close > a;  short_cond = mirror (close < a);  a_f = a / a[1] between 0.999 and 1.001 (the KAMA is flat)
    long_stop = (SMA1 < SMA2 < SMA3) and trend SMA < close;  short_stop = (SMA1 > SMA2 > SMA3) and trend SMA > close;  entry Long / Short;  close_all when long_stop or short_stop

Interpretation choices (Pine rules in SURVEY_README.md)
    * KAMA: er = |change(close, n)| / sum(|change(close)|, n); with "Self Powered" the smoothing is er ^ (1 / er)
      (else er ^ 2); a = per * close + (1 - per) * nz(a[1], close). The long entry, the short entry and
      the close_all conditions cannot hold on the same bar (the alignments and the trend side exclude one
      another), so the order of the three does not matter. REVERSAL INTENDED. The cash quantity is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average alignment and adaptive average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND433101 (2 members, best partner #433101, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436491_three_sma_kama_alignment"
FAMILY = "trend_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma1": [16, 12],
    "kama_len": [50, 30],
}
DEFAULT_PARAMS = {"sma1": 16, "sma2": 36, "sma3": 72, "trend": 100, "kama_len": 50, "self_powered": True}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s1 = c.rolling(int(p["sma1"])).mean()
    s2 = c.rolling(int(p["sma2"])).mean()
    s3 = c.rolling(int(p["sma3"])).mean()
    long_ma, short_ma = (s1 > s2) & (s2 > s3), (s1 < s2) & (s2 < s3)
    trend = c.rolling(int(p["trend"])).mean()
    n = int(p["kama_len"])
    signal = c.diff(n).abs()
    noise = c.diff().abs().rolling(n).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        er = (signal / noise.where(noise != 0)).to_numpy()
        pw = 1.0 / er if p["self_powered"] else np.full(len(er), 2.0)
        per = er ** pw
    x = c.to_numpy(dtype=float)
    m = len(x)
    a = np.full(m, np.nan)
    for i in range(m):
        if np.isnan(per[i]):
            continue
        prev = a[i - 1] if i > 0 and not np.isnan(a[i - 1]) else x[i]
        a[i] = per[i] * x[i] + (1.0 - per[i]) * prev
    a1 = np.concatenate(([np.nan], a[:-1]))
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = a / a1
        a_f = (ratio > 0.999) & (ratio < 1.001)
        long_c = long_ma.to_numpy() & (trend.to_numpy() < x) & ~a_f & (x > a)
        short_c = short_ma.to_numpy() & (trend.to_numpy() > x) & ~a_f & (x < a)
    stop = (short_ma & (trend < c)) | (long_ma & (trend > c))
    ix = bars_df.index
    return pd.Series(long_c, index=ix), stop, pd.Series(short_c, index=ix), stop.copy()


def portfolio_kwargs(**params):
    return {}
