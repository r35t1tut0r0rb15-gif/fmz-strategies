"""A hand-built band line (SMA 10 -/+ 3 ATR 10, flipping on the close against its last value) with RSI 14, hourly bars: the close over the line with RSI over 30 goes long, under it with RSI under 70 goes short; reversing.
Port of FMZ strategy #483027 "动态趋势RSI交叉动量增强策略-Dynamic-Trend-RSI-Crossover-Momentum-Enhancement-Strategy" (Supertrend + RSI Strategy).

FMZ source id: 483027

Source
    https://www.fmz.com/strategy/483027 (PineScript v5, FMZ last modified 2025-02-21 10:00:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-148), ATR 10; factor 3; SMA 10 bands; RSI 14 / 70 / 30
    supertrend = close > nz(supertrend[1], close) ? sma10 - 3 atr : sma10 + 3 atr;  signal = close > supertrend ? Buy : Sell
    signal Buy and rsi > 30 -> entry Long;  signal Sell and rsi < 70 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is not Pine's ta.supertrend: it takes the lower band whenever the close is over the
      line's previous value and the upper band otherwise, as written (the first bar compares the close
      with itself and takes the upper band). The conditions are states; a repeat on the side held adds
      nothing, the other side reverses (REVERSAL INTENDED). No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-line side with RSI filters.
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

NAME = "fmz_483027_sma10_atr3_flip_line_side_rsi14_state_reversal"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_length": [10, 20],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_length": 10, "factor": 3.0, "rsi_length": 14, "rsi_ob": 70, "rsi_os": 30}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["atr_length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, n)
    ma = c.rolling(n).mean()
    k = float(p["factor"])
    ub, lb = (ma + k * atr).to_numpy(), (ma - k * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    st = np.full(m, np.nan)
    for i in range(m):
        prev = st[i - 1] if i >= 1 and not np.isnan(st[i - 1]) else cv[i]   # nz(supertrend[1], close)
        st[i] = lb[i] if cv[i] > prev else ub[i]
    buy = pd.Series(cv > st, index=c.index)
    r = _rsi(c, int(p["rsi_length"]))
    le = buy & (r > float(p["rsi_os"]))
    se = ~buy & (r < float(p["rsi_ob"]))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
