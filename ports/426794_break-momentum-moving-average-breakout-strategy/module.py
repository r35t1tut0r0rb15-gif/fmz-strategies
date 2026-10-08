"""Momentum + EMA 5: three bars in a row with 5-bar momentum above a threshold and the close above
EMA 5 go long; three with momentum below the same threshold and the close below EMA 5 go short.
Each entry has a profit target; the source's tick trailing stop is pending (rule 2).
Port of FMZ strategy #426794 "Momentum Moving Average Breakout Strategy".

Source
    https://www.fmz.com/strategy/426794 (PineScript v5, FMZ last modified 2023-09-14 16:06:41).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 116-124), momentum 5 vs 50, EMA 5
    mom(close, 5), mom(close[1], 5), mom(close[2], 5) > 50 and close > ema(close, 5) -> entry long
    the same three < 50 and close < ema(close, 5)                                 -> entry short
    each: exit(profit = 1000 ticks, trail_points = 60 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the short threshold is +50 too (not -50): shorts need momentum under +50.
    * Criterion 2: 50 is a price distance (BTC: 50 USDT) and becomes mom_atr x ATR(14); the
      1000-tick target becomes tp_atr x ATR(14) at the signal bar (a tp_stop fraction shifted
      one bar).
    * The trailing stop (trail_points = 60 ticks, no trail_offset; Pine needs both to arm a
      trail, so as written it may never arm) is rule 2: trailing_stop_pending, not emitted.
      See PORT_NOTES.
    * Entries do not depend on the position: no mirroring. REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426794_momentum_ema5"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "mom_atr": [0.25, 0.5, 1.0],
    "tp_atr": [0.5, 1.0, 2.0],
}
DEFAULT_PARAMS = {"mom_len": 5, "ema_len": 5, "mom_atr": 0.25, "tp_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _signals(bars_df, p):
    c = bars_df["close"]
    k = int(p["mom_len"])
    mom = c - c.shift(k)
    thr = p["mom_atr"] * _atr_pine(bars_df, ATR_LEN)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    above = (mom > thr) & (mom.shift(1) > thr) & (mom.shift(2) > thr)
    below = (mom < thr) & (mom.shift(1) < thr) & (mom.shift(2) < thr)
    return above & (c > ema), below & (c < ema)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    frac = (p["tp_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(le | se)
    return {"tp_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
