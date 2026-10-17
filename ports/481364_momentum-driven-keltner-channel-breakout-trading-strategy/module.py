"""Closes crossing out of the Keltner channel (EMA 20 -/+ 1.5 ATR 20) with 14-bar momentum on the same side go long /
short; a cross back through the EMA or momentum turning closes the trade, fifteen-minute bars.
Port of FMZ strategy #481364 "动量驱动型肯特纳通道突破交易策略-Momentum-Driven-Keltner-Channel-Breakout-Trading-Strategy" (Keltner Channels + Momentum Strategy).

FMZ source id: 481364

Source
    https://www.fmz.com/strategy/481364 (PineScript v5, FMZ last modified 2025-02-10 15:03:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 150-192), KC 20 x 1.5, momentum 14
    crossover(close, upper) and mom > 0 -> entry long; crossunder(close, lower) and mom < 0 -> entry short
    crossunder(close, ema) or mom < 0 -> close long; crossover(close, ema) or mom > 0 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a Keltner channel and momentum signs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity, quoted in original_sizing.txt.
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

NAME = "fmz_481364_keltner_break_momentum_ema_exit"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 2.5],
    "mom_len": [14, 28],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.5, "mom_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    ema = c.ewm(span=n, adjust=False).mean()
    band = p["mult"] * _atr(bars_df, n)
    upper, lower = ema + band, ema - band
    mom = c - c.shift(int(p["mom_len"]))

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    buy = (xover(c, upper) & (mom > 0)).to_numpy()
    sell = (xover(lower, c) & (mom < 0)).to_numpy()
    xl = (xover(ema, c) | (mom < 0)).to_numpy()
    xs = (xover(c, ema) | (mom > 0)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and pos != -1:
            se[i], pos = True, -1
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
