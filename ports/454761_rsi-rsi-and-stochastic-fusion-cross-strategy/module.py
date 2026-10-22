"""Stacked RSI / stochastic turns, 2-hour bars: a rising RSI 14 of ohlc4 under 37 crossing over its SMA 14 under 40, with a stochastic %K / %D cross up under 20, goes long; the mirror (falling RSI over 49 crossing under its SMA over 60, a %K cross down over 80) goes short; reversing.
Port of FMZ strategy #454761 "RSI与随机指标融合交叉策略-RSI-and-Stochastic-Fusion-Cross-Strategy" (-VrilyaSS-RSI&SToch-Cross+2xRSI+2xStoch-Lines+RSI-SMA-Cross-V4-).

FMZ source id: 454761

Source
    https://www.fmz.com/strategy/454761 (PineScript v5, FMZ last modified 2024-06-21 17:55:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 166-242), RSI 14 of ohlc4, lines 37 / 49; RSI SMA 14, lines 40 / 60; stochastic 14 / 3 / 3, lines 20 / 80
    rsi up and rsi < 37 and crossover(%K, %D) and %K < 20 and crossover(rsi, sma(rsi, 14)) and rsi < 40 -> entry Buy
    rsi down and rsi > 49 and crossunder(%K, %D) and %K > 80 and crossunder(rsi, sma(rsi, 14)) and rsi > 60 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * All five tests must hold on one bar. The smoothed RSI is the SMA 14 of the RSI of ohlc4 (the
      same RSI). There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing
      code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked RSI / stochastic turns.
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

NAME = "fmz_454761_rsi_stoch_stacked_turn_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "k_len": [14, 7],
}
DEFAULT_PARAMS = {"rsi_len": 14, "k_len": 14, "sma_len": 14}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    r = _rsi(src, int(p["rsi_len"]))
    rs = r.rolling(int(p["sma_len"])).mean()
    n = int(p["k_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = (100 * (c - ll) / rng.where(rng > 0)).rolling(3).mean()
    d = k.rolling(3).mean()
    k_up = (k > d) & (k.shift(1) <= d.shift(1))
    k_dn = (k < d) & (k.shift(1) >= d.shift(1))
    r_up_x = (r > rs) & (r.shift(1) <= rs.shift(1))
    r_dn_x = (r < rs) & (r.shift(1) >= rs.shift(1))
    dr = r.diff()
    le = (dr > 0) & (r < 37) & k_up & (k < 20) & r_up_x & (r < 40)
    se = (dr < 0) & (r > 49) & k_dn & (k > 80) & r_dn_x & (r > 60)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
