"""SMA 150 +/- 4 ATR(30) channel breakouts, 30-minute bars: the close crossing over the upper band goes long, crossing under the lower band goes short; the close crossing back through the SMA closes; reversing.
Port of FMZ strategy #439715 "基于ATR通道突破的量化交易策略An-ATR-Channel-Breakout-Quantitative-Trading-Strategy" (ATR Channel Breakout).

FMZ source id: 439715

Source
    https://www.fmz.com/strategy/439715 (PineScript v5, FMZ last modified 2024-01-23 12:00:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-203), SMA 150; ATR 30; offsets 4 / 4
    enterLong = crossover(close, sma + 4 atr);  exitLong = crossunder(close, sma);  enterShort = crossunder(close, sma - 4 atr);  exitShort = crossover(close, sma)
    entry Long / entry Short, then close Long / close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come after the entries: a short entry on the bar a long's close also fires reverses
      and the reversal stands (as #438020); a held position meeting its close ends flat. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR channel and SMA crossings.
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

NAME = "fmz_439715_sma150_atr_channel_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "offset": [4.0, 2.0],
    "sma_length": [150, 50],
}
DEFAULT_PARAMS = {"offset": 4.0, "sma_length": 150, "atr_length": 30}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = c.rolling(int(p["sma_length"])).mean()
    a = _atr(bars_df, p["atr_length"])
    ub, lb = s + float(p["offset"]) * a, s - float(p["offset"]) * a

    def xo(x, y):
        return ((x > y) & (x.shift(1) <= y.shift(1))).to_numpy()

    el, es = xo(c, ub), xo(lb, c)
    xl, xs = xo(s, c), xo(c, s)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if el[i] and pos != 1:
            new = 1
        elif es[i] and pos != -1:
            new = -1
        if pos == 1 and xl[i] and new == 1:
            new = 0
        if pos == -1 and xs[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
