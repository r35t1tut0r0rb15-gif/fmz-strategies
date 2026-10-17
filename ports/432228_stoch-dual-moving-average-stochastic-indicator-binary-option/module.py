"""EMA-band fades with a stochastic filter, 3-minute bars: a close under the EMA 4 of the lows and the EMA 21, an open under
the bands' middle, and the stochastic K (14) and D (3) under 50 go long; the mirror above the EMA 4 of the highs goes
short; always in once started.
Port of FMZ strategy #432228 "双均线Stoch指标二元期权交易策略Dual-Moving-Average-Stochastic-Indicator-Binary-Options-Trading-Strategy" (Binary Option EMA/Stoch strategy Corrected).

FMZ source id: 432228

Source
    https://www.fmz.com/strategy/432228 (PineScript v2, FMZ last modified 2023-11-15 16:56:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 207-239), stoch 14 / 1 / 3, EMA 4 of high, EMA 4 of low, EMA 21
    x = close < ema(low, 4) and open < (ema(high, 4) + ema(low, 4)) / 2 and close < ema(close, 21) and d < 50 and k < 50 -> entry long ("UP")
    y = close > ema(high, 4) and open > mid and close > ema(close, 21) and d > 50 and k > 50 -> entry short ("DOWN")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weak-side condition opens the long and the strong-side condition the short, as written (a
      fade). k = sma(stoch(14), 1) is the raw stochastic.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA bands and stochastic levels.
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

NAME = "fmz_432228_ema_band_stoch_fade"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "band_len": [4, 8],
    "ema_len": [21, 50],
}
DEFAULT_PARAMS = {"stoch_len": 14, "smooth_k": 1, "smooth_d": 3, "band_len": 4, "ema_len": 21}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    b = int(p["band_len"])
    hi_b = h.ewm(span=b, adjust=False).mean()
    lo_b = lo.ewm(span=b, adjust=False).mean()
    mid = (hi_b + lo_b) / 2
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    x = ((c < lo_b) & (o < mid) & (c < e) & (d < 50) & (k < 50)).to_numpy()
    y = ((c > hi_b) & (o > mid) & (c > e) & (d > 50) & (k > 50)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
