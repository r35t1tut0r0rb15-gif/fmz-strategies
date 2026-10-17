"""Outer Fibonacci Keltner band breakouts, 1-hour bars: hl2 crossing above the WMA 233 + 4.236 x 2 x ATR band with the RSI 14
of hl2 over 60 goes long, crossing under the lower band with it under 40 goes short; hl2 crossing the WMA back closes
everything.
Port of FMZ strategy #432811 "基于斐波那契通道的K线反转策略Fibonacci-Channel-Based-Candlestick-Reversal-Trading-Strategy" ([blackcat] L2 Fibonacci Bands).

FMZ source id: 432811

Source
    https://www.fmz.com/strategy/432811 (PineScript v5, FMZ last modified 2023-11-21 17:24:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-234), WMA 233 of hl2, KC 89 x 2 (SMA of the true range), Fibonacci 4.236, RSI 14 of hl2
    upper3 = wma + 4.236 x (2 x sma(tr, 89));  lower3 mirror
    crossover(hl2, upper3) and rsi(hl2, 14) > 60 -> entry long;  crossunder(hl2, lower3) and rsi < 40 -> entry short
    cross(hl2, wma) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the outer band (level 3) trades; the inner bands draw. The final close_all acts on the
      position held at the bar's start and leaves the bar flat (C31-C39 convention).
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands, an RSI filter and WMA crosses.
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

NAME = "fmz_432811_fibonacci_keltner_outer_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fib": [4.236, 2.618],
    "ma_len": [233, 89],
}
DEFAULT_PARAMS = {"ma_len": 233, "kc_len": 89, "kc_mult": 2.0, "fib": 4.236, "rsi_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo) / 2
    ma = _wma(src, int(p["ma_len"]))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    band = float(p["fib"]) * float(p["kc_mult"]) * tr.rolling(int(p["kc_len"])).mean()
    up3, lo3 = ma + band, ma - band
    d = src.diff()
    ru = d.clip(lower=0).ewm(alpha=1 / int(p["rsi_len"]), adjust=False).mean()
    rd = (-d.clip(upper=0)).ewm(alpha=1 / int(p["rsi_len"]), adjust=False).mean()
    r = 100 - 100 / (1 + ru / rd)
    x = ((src > up3) & (src.shift(1) <= up3.shift(1)) & (r > 60)).to_numpy()
    y = ((src < lo3) & (src.shift(1) >= lo3.shift(1)) & (r < 40)).to_numpy()
    ex = (((src > ma) & (src.shift(1) <= ma.shift(1))) | ((src < ma) & (src.shift(1) >= ma.shift(1)))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        if ex[i]:
            pos = 0                                       # the final close_all leaves the bar flat
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
