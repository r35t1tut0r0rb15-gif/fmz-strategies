"""Profit Maximizer (PMax) crossings with a ZLEMA, 5-minute bars, long only: the ZLEMA 10 of hl2 crossing over its ATR(10) x 3 PMax line buys, crossing under sells the position (flat).
Port of FMZ strategy #439094 "Momentum Breakout Optimization" (Profit Maximizer PMax).

FMZ source id: 439094

Source
    https://www.fmz.com/strategy/439094 (PineScript v4, FMZ last modified 2024-01-17 16:44:30).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 206-358), source hl2; ATR 10 (Wilder) x 3; MA ZLEMA 10; crossing signals on, price signals off; risk sizing 0.5 %; dates true
    MAvg = ema(src + (src - src[5]), 10);  longStop / shortStop ratchets and dir as PMax;  crossover(MAvg, PMax) -> entry buySignalk (risk qty);  crossunder -> order(sellSignallk, short, qty = position size)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sell is a strategy.order for the open quantity, so it only flattens a long (with no position it
      sends nothing); the price / PMax signals are off, so no short is opened. inDateRange is true. The
      risk-based quantity is sizing; the commission and slippage are costs. Long only. FREQ = "5min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ZLEMA and ATR stop line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity, capital, commission and slippage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND365691 (3 members, best partner #365691, Jaccard 0.670); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439094_pmax_zlema_cross_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [3.0, 2.0],
    "length": [10, 20],
}
DEFAULT_PARAMS = {"multiplier": 3.0, "length": 10, "periods": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["periods"])).to_numpy()
    src = (h + lo) / 2
    n = int(p["length"])
    lag = n // 2 if n % 2 == 0 else (n - 1) // 2
    mav = (src + (src - src.shift(lag))).ewm(span=n, adjust=False).mean().to_numpy()
    k = float(p["multiplier"])
    m = len(mav)
    ls, ss = np.full(m, np.nan), np.full(m, np.nan)
    pm = np.full(m, np.nan)
    d = 1
    for i in range(m):
        l0, s0 = mav[i] - k * atr[i], mav[i] + k * atr[i]
        lp = ls[i - 1] if i > 0 and not np.isnan(ls[i - 1]) else l0           # nz(longStop[1], longStop)
        sp = ss[i - 1] if i > 0 and not np.isnan(ss[i - 1]) else s0
        ls[i] = max(l0, lp) if (mav[i] > lp and not np.isnan(l0)) else l0
        ss[i] = min(s0, sp) if (mav[i] < sp and not np.isnan(s0)) else s0
        if d == -1 and mav[i] > sp:
            d = 1
        elif d == 1 and mav[i] < lp:
            d = -1
        pm[i] = ls[i] if d == 1 else ss[i]
    ms, ps = pd.Series(mav, index=c.index), pd.Series(pm, index=c.index)
    up = (ms > ps) & (ms.shift(1) <= ps.shift(1))
    dn = (ms < ps) & (ms.shift(1) >= ps.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
