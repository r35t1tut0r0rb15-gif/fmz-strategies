"""Closes crossing over the EMA 20 while the EMA 20, 50 and 100 all rise, 4-hour bars, long only: entered from flat; RSI 14 over 70 or the close crossing under the EMA 20 closes.
Port of FMZ strategy #482502 "多周期均线趋势判断与RSI超买策略-Multi-Period-EMA-Trend-Detection-with-RSI-Overbought-Strategy" (EMA Crossover + RSI Strategy).

FMZ source id: 482502

Source
    https://www.fmz.com/strategy/482502 (PineScript v5, FMZ last modified 2025-02-18 17:50:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-138), EMA 20 / 50 / 100 rising; RSI 14 > 70 exit; 200 % of equity; capital 10000
    crossover(close, ema20) and ema20, ema50, ema100 all above their previous values -> entry Long;  rsi > 70 or crossunder(close, ema20) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * An entry and a close can both be true on one bar (an up-crossing with RSI over 70): the entry comes
      first, so from flat the entry stands and the close does not act on it; when a long is held into the
      bar the entry is ignored and the close acts (as #441963): a loop. Long only. The 200 % of equity size
      and capital are sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 20 re-crossings in a rising EMA stack with RSI / EMA exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482502_close_ema20_cross_rising_ema_stack_rsi70_exit_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_exit": [70, 80],
    "ema_entry": [20, 10],
}
DEFAULT_PARAMS = {"rsi_exit": 70, "ema_entry": 20, "rsi_length": 14}


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
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    e1, e50, e100 = ema(p["ema_entry"]), ema(50), ema(100)
    rising = (e1 > e1.shift(1)) & (e50 > e50.shift(1)) & (e100 > e100.shift(1))
    r = _rsi(c, int(p["rsi_length"]))
    lc = ((c > e1) & (c.shift(1) <= e1.shift(1)) & rising).to_numpy()
    xc = ((r > float(p["rsi_exit"])) | ((c < e1) & (c.shift(1) >= e1.shift(1)))).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xc[i]:
            lx[i], pos = True, 0                  # the close acts on the long held into the bar
        elif pos == 0 and lc[i]:
            le[i], pos = True, 1
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
