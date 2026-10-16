"""Bollinger band extremes with a stochastic-RSI turn, 1-minute bars: K crossing above D with the close under the lower band
(20, 2) goes long; K crossing below D with the close over the upper band goes short.
Port of FMZ strategy #430597 "布林线与StochRSI动量策略Bollinger-Bands-and-StochRSI-Momentum-Strategy" (My Strategy with Bollinger Bands and StochRSI).

FMZ source id: 430597

Source
    https://www.fmz.com/strategy/430597 (PineScript v5, FMZ last modified 2023-10-30 17:19:21).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 203-248), BB 20 / 2, RSI 14, stochastic of RSI over 3 bars, K 3, D 3
    rsi = rsi(close, 14); k = sma(stoch(rsi, rsi, rsi, 3), 3); d = sma(k, 3)
    crossover(k, d) and close < lowerBB -> entry long;  crossunder(k, d) and close > upperBB -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stochastic of RSI uses k_period (3) as its length, as written (not the RSI length).
      stdev is the population deviation.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and a stochastic RSI.
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

NAME = "fmz_430597_bb_stochrsi_turns"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "bb_dev": [2.0, 2.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_dev": 2.0, "rsi_len": 14, "k_period": 3, "d_period": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up_b, lo_b = basis + p["bb_dev"] * sd, basis - p["bb_dev"] * sd
    r = _rsi(c, int(p["rsi_len"]))
    kp = int(p["k_period"])
    ll, hh = r.rolling(kp).min(), r.rolling(kp).max()
    k = (100 * (r - ll) / (hh - ll).replace(0.0, np.nan)).rolling(kp).mean()
    d = k.rolling(int(p["d_period"])).mean()
    buy = ((k > d) & (k.shift(1) <= d.shift(1)) & (c < lo_b)).to_numpy()
    sell = ((k < d) & (k.shift(1) >= d.shift(1)) & (c > up_b)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif sell[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
