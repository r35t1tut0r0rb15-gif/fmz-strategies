"""Triple EMA cross with a momentum buffer, 1-minute bars: EMA 5 crossing above EMA 20 with both and the close above
EMA 50 and the close a buffer above the previous close goes long; the mirror goes short (the coded stop is never
passed to an order).
Port of FMZ strategy #429478 "三重EMA追踪止损策略Triple-EMA-With-Trailing-Stop-Loss-Strategy" (Triple EMA Strategy).

FMZ source id: 429478

Source
    https://www.fmz.com/strategy/429478 (PineScript v4, FMZ last modified 2023-10-17 15:05:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-213), EMA 5 / 20 / 50, buffer 15 ticks (FX: 1.5 pips), stop 100 / trail 130 ticks
    long = crossover(ema5, ema20) and close > ema50 and ema5 > ema50 and ema20 > ema50 and close > close[1] + buffer -> entry long
    short = mirror with close < close[1] - buffer -> entry short
    StopLoss is updated in a variable, but every strategy.exit(...) call has no stop / limit argument: inert

Interpretation choices (Pine rules in SURVEY_README.md)
    * The StopLoss variable never reaches an order (strategy.exit without price arguments places
      nothing), so positions change only on the opposite entry.
    * Criterion 2: the buffer of 15 / (1000 x 100) = 0.00015 (1.5 pips on a 5-digit FX pair, the author's
      Oanda setting) becomes buffer_atr x Wilder ATR(14); 1.5 pips on 1-minute EURUSD is about 0.75 ATR
      (judgement before any backtest).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the pip buffer -> an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() cash quantity and the inert stop inputs stored.
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

NAME = "fmz_429478_triple_ema_buffer"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buffer_atr": [0.75, 0.25],
    "ema3": [50, 100],
}
DEFAULT_PARAMS = {"ema1": 5, "ema2": 20, "ema3": 50, "buffer_atr": 0.75, "atr_length": 14}


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
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    e1, e2, e3 = e(p["ema1"]), e(p["ema2"]), e(p["ema3"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    buf = p["buffer_atr"] * _rma(tr, int(p["atr_length"]))
    long_e = ((e1 > e2) & (e1.shift(1) <= e2.shift(1)) & (c > e3) & (e1 > e3) & (e2 > e3)
              & (c > pc + buf)).astype(bool)
    short_e = ((e1 < e2) & (e1.shift(1) >= e2.shift(1)) & (c < e3) & (e1 < e3) & (e2 < e3)
               & (c < pc - buf)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
