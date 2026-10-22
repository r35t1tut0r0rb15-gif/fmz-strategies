"""EMA 50 / SMA 100 crossings with RSI exits, 1-hour bars: the EMA 50 crossing over the SMA 100 goes long, under goes short; the RSI 14 at 70 or more closes the long, at 30 or less closes the short;
reversing.
Port of FMZ strategy #443119 "基于EMA均线和RSI指标的量化交易策略EMA-and-RSI-Quantitative-Trading-Strategy" (Estrategia de Trading (EMA 50 / SMA 100 with RSI exits)).

FMZ source id: 443119

Source
    https://www.fmz.com/strategy/443119 (PineScript v4, FMZ last modified 2024-02-29 13:52:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-174), EMA 50, SMA 100; RSI 14 (70 / 30)
    crossover(ema50, sma100) -> entry Buy;  crossunder -> entry Sell;  rsi >= 70 -> close Buy;  rsi <= 30 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported in call order with one position at a time; each close acts only on a held position.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA / SMA crossings with RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG443119 (2 members, best partner #443244, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443119_ema50_sma100_cross_rsi_exits"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "overbought": [70, 80],
}
DEFAULT_PARAMS = {"rsi_length": 14, "overbought": 70, "ema_len": 50, "sma_len": 100}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    s = c.rolling(int(p["sma_len"])).mean()
    lg = ((e > s) & (e.shift(1) <= s.shift(1))).to_numpy()
    sh = ((e < s) & (e.shift(1) >= s.shift(1))).to_numpy()
    r = _rsi(c, int(p["rsi_length"]))
    ob = float(p["overbought"])
    xl = (r >= ob).to_numpy()
    xs = (r <= 100.0 - ob).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
