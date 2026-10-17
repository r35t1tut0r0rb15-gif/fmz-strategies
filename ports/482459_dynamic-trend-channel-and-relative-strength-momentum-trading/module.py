"""Closes crossing up through the lower Keltner channel (EMA 20 -/+ 1.5 ATR 10) with RSI below 30 go long, crossing
down through the upper channel with RSI above 70 go short; the EMA cross-back or RSI across 50 closes the trade,
three-hour bars.
Port of FMZ strategy #482459 "动态趋势通道与相对强弱指标相结合的量化交易策略-Dynamic-Trend-Channel-and-Relative-Strength-Momentum-Trading-Strategy" (Keltner Channel + RSI Strategy).

FMZ source id: 482459

Source
    https://www.fmz.com/strategy/482459 (PineScript v6, FMZ last modified 2025-02-18 15:15:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-147), EMA 20, ATR 10 x 1.5, RSI 14 (70 / 30)
    crossover(close, lower) and rsi < 30 -> entry long; crossunder(close, upper) and rsi > 70 -> entry short
    crossunder(close, ema) or rsi > 50 -> close long; crossover(close, ema) or rsi < 50 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a Keltner channel and RSI levels.
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

NAME = "fmz_482459_keltner_reentry_rsi_extreme_mid_exit"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [1.5, 2.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"ema_len": 20, "atr_len": 10, "multiplier": 1.5, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    band = p["multiplier"] * _atr(bars_df, int(p["atr_len"]))
    upper, lower = ema + band, ema - band
    rsi = _rsi(c, int(p["rsi_len"]))

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    buy = (xover(c, lower) & (rsi < p["os"])).to_numpy()
    sell = (xover(upper, c) & (rsi > p["ob"])).to_numpy()
    xl = (xover(ema, c) | (rsi > 50)).to_numpy()
    xs = (xover(c, ema) | (rsi < 50)).to_numpy()
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
