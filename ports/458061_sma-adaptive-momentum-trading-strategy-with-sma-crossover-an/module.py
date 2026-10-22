"""SMA 20 / 50 crossings in the direction of the classic Supertrend (ATR 10 x 3), 2-hour bars: the cross up in an up trend goes long, the cross down in a down trend goes short, each with a 1 % target from the fill; reversing.
Port of FMZ strategy #458061 "SMA交叉结合超趋势的自适应动量交易策略Adaptive-Momentum-Trading-Strategy-with-SMA-Crossover-and-SuperTrend" (SMA Crossover with Supertrend).

FMZ source id: 458061

Source
    https://www.fmz.com/strategy/458061 (PineScript v5, FMZ last modified 2024-07-29 16:38:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-257), SMA 20 / 50; Supertrend ATR 10 (rma), multiplier 3, hl2; target 1 % of the average price (no stop)
    crossover(sma20, sma50) and trend == 1 -> entry Long;  crossunder and trend == -1 -> entry Short;  exit(limit = avg x 1.01) / exit(limit = avg x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The classic Supertrend recursion as written. The targets are sent every bar from the average
      (fill) price: ported active from the fill bar (#440797) as the fixed fraction 0.01 of the fill;
      there is no stop. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour
      bars: mark coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned
      2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price target as a fixed fraction.
    2 generic: PASS, SMA crossings with a Supertrend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458061_sma20_50_cross_supertrend_target_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma1": [20, 10],
    "sma2": [50, 100],
    "tp_pct": [0.01, 0.03],
}
DEFAULT_PARAMS = {"sma1": 20, "sma2": 50, "tp_pct": 0.01, "atr_len": 10, "mult": 3.0}


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


def _classic_trend(bars_df, n, k):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(n)).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upv, dnv, trend = np.full(m, np.nan), np.full(m, np.nan), np.ones(m, dtype=int)
    t = 1
    for i in range(m):
        up, dn = hl2[i] - k * atr[i], hl2[i] + k * atr[i]
        up1 = upv[i - 1] if i > 0 and not np.isnan(upv[i - 1]) else up
        dn1 = dnv[i - 1] if i > 0 and not np.isnan(dnv[i - 1]) else dn
        cp = cv[i - 1] if i > 0 else np.nan
        if cp > up1:
            up = max(up, up1)
        if cp < dn1:
            dn = min(dn, dn1)
        if t == -1 and cv[i] > dn1:
            t = 1
        elif t == 1 and cv[i] < up1:
            t = -1
        upv[i], dnv[i], trend[i] = up, dn, t
    return trend


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    tr = pd.Series(_classic_trend(bars_df, p["atr_len"], float(p["mult"])), index=c.index)
    a, b = c.rolling(int(p["sma1"])).mean(), c.rolling(int(p["sma2"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (tr == 1)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (tr == -1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
