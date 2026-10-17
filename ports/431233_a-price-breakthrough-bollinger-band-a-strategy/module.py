"""Bollinger re-entry with a stochastic RSI floor, 1-minute bars: the close crossing back above the lower band (21, 1.5)
with stochastic RSI K and D at or under 20 and a rising EMA 7 goes long; the close crossing above the upper band goes
short.
Port of FMZ strategy #431233 "价格突破布林线A策略Price-Breakthrough-Bollinger-Band-A-Strategy" (Bollinger e Tendência).

FMZ source id: 431233

Source
    https://www.fmz.com/strategy/431233 (PineScript v3, FMZ last modified 2023-11-06 11:43:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 177-336), BB 21 / 1.5, stoch RSI 11 / 7 / 3 / 4, EMA 7
    compra = crossover(close, lowerBol) and k <= 20 and d <= 20 and ema(close, 7) > ema(close, 7)[1] -> entry long
    venda = crossover(close, upperBol) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The candle patterns, the daily pivot colours and the band-width input are plot-only (the
      pattern entries are commented out). stdev is the population deviation.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands, stochastic RSI and an EMA slope.
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

NAME = "fmz_431233_bb_stoch_rsi_reentry"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 21, "mult": 1.5, "rsi_len": 11, "stoch_len": 7, "smooth_k": 3, "smooth_d": 4,
                  "ema_len": 7}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + p["mult"] * sd, basis - p["mult"] * sd
    r = _rsi(c, int(p["rsi_len"]))
    s = int(p["stoch_len"])
    lo_, hi_ = r.rolling(s).min(), r.rolling(s).max()
    k = (100 * (r - lo_) / (hi_ - lo_).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    buy = ((c > lower) & (c.shift(1) <= lower.shift(1)) & (k <= 20) & (d <= 20) & (ema > ema.shift(1))).to_numpy()
    sell = ((c > upper) & (c.shift(1) <= upper.shift(1))).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        if sell[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
