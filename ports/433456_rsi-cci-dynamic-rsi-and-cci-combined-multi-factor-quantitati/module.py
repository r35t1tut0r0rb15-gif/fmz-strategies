"""Stochastic-RSI pull-back longs in an SMA uptrend, 1-minute bars, long only: with the SMA 12 above the SMA 26, CCI 26 under
100, both stochastic RSIs (14 / 14 / 3 / 3 and 5 / 5 / 4 / 3) under 80 and the fast one's K crossing above its D, a long
opens; a weighted RSI crossing under its dynamic upper line while the slow K is above 80 closes it.
Port of FMZ strategy #433456 "动态RSI与CCI结合的多因子量化交易策略Dynamic-RSI-and-CCI-Combined-Multi-factor-Quantitative-Trading-Strategy" (ATOM2.0).

FMZ source id: 433456

Source
    https://www.fmz.com/strategy/433456 (PineScript v4, FMZ last modified 2023-11-27 18:54:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 147-227), SMA 12 / 26; stoch RSI 14 / 14 / 3 / 3 and 5 / 5 / 4 / 3; CCI 26; dynamic zone RSI 14, lookback 60, 0.1; pyramiding 10
    buy = sma12 > sma26 and cci < 100 and k < 80 and d < 80 and k2 < 80 and d2 < 80 and crossover(k2, d2) -> entry long (adds up to 10)
    R = (4 rsi + 3 rsi[1] + 2 rsi[2] + rsi[3]) / 10;  jh / jl = highest / lowest(rsi, 60);  jc = wma((jh - jl) / 2, 14) + wma(jl, 14);  Hiline = jh - 0.1 jc
    crossunder(R, Hiline) and k > 80 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 10 adds further units on repeated signals; stacking is sizing (SURVEY_README, as
      #426588), so the net position is ported: long from the first signal until the close.
    * The fund x leverage / close quantity is sizing. Long only; Opposite entries cannot occur.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average order and oscillator levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fund x leverage quantity and pyramiding 10 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433456_stoch_rsi_pullback_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [12, 24],
    "slow_ma": [26, 52],
}
DEFAULT_PARAMS = {"fast_ma": 12, "slow_ma": 26, "cci_len": 26}


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
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())


def _stoch_rsi(c, rl, sl, ks, ds):
    r = _rsi(c, rl)
    lo, hi = r.rolling(sl).min(), r.rolling(sl).max()
    k = (100 * (r - lo) / (hi - lo)).rolling(ks).mean()
    return k, k.rolling(ds).mean()


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (w / w.sum())
    return pd.Series(out, index=x.index)


def _cci(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        mu = win.mean(axis=1)
        md = np.abs(win - mu[:, None]).mean(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[n - 1:] = (v[n - 1:] - mu) / (0.015 * md)
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    m12 = c.rolling(int(p["fast_ma"])).mean()
    m26 = c.rolling(int(p["slow_ma"])).mean()
    k, d = _stoch_rsi(c, 14, 14, 3, 3)
    k2, d2 = _stoch_rsi(c, 5, 5, 4, 3)
    cci = _cci(c, int(p["cci_len"]))
    rl = _rsi(c, 14)
    jh, jl = rl.rolling(60).max(), rl.rolling(60).min()
    jc = _wma((jh - jl) * 0.5, 14) + _wma(jl, 14)
    hil = jh - jc * 0.1
    r = (4 * rl + 3 * rl.shift(1) + 2 * rl.shift(2) + rl.shift(3)) / 10
    buy = ((m12 > m26) & (cci < 100) & (k < 80) & (d < 80) & (k2 < 80) & (d2 < 80)
           & (k2 > d2) & (k2.shift(1) <= d2.shift(1))).to_numpy()
    ex = ((r < hil) & (r.shift(1) >= hil.shift(1)) & (k > 80)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif pos == 1 and ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
