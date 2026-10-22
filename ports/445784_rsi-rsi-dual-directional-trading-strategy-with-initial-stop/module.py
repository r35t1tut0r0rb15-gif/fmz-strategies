"""RSI 14 crossings of 60 and 40, 1-hour bars: the RSI reaching 60 from below goes long and falling back to 60 closes it; reaching 40 from above goes short and rising back to 40 closes it; reversing (the
6 % stop from each bar's close is re-sent every bar and is not ported).
Port of FMZ strategy #445784 "RSI双向交易策略与初始止损RSI-Dual-Directional-Trading-Strategy-with-Initial-Stop-Loss" (RSI Long and Short Strategy with Initial Stop Loss).

FMZ source id: 445784

Source
    https://www.fmz.com/strategy/445784 (PineScript v5, FMZ last modified 2024-03-22 10:44:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-220), RSI 14 from the "60" time frame (the chart's own); levels 60 / 40; initial stop 6 % of the current close; 100 % of equity
    rsi[1] < 60 and rsi >= 60 -> entry Long;  rsi[1] > 60 and rsi <= 60 -> close Long;  rsi[1] > 40 and rsi <= 40 -> entry Short;  rsi[1] < 40 and rsi >= 40 -> close Short
    exit(Long, stop = close x 0.94);  exit(Short, stop = close x 1.06)  (called every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 60-minute request on a 1-hour chart returns the chart's own RSI. The "initial" stop is
      re-sent on every bar at 6 % from that bar's close, so it moves with the price after entry (up or
      down): stops() cannot express it, so it is not ported (mark trailing_stop_pending; the intended
      stop is owed); the RSI exits and the opposite entries end the positions meanwhile. Calls run in
      order: a close called after the opposite entry on the same bar leaves the reversal. REVERSAL
      INTENDED. The 100 % of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop not ported (mark).
    2 generic: PASS, RSI level crossings with RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored; the 6 % stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_445784_rsi_60_40_cross_rsi_exit_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "upper": [60, 70],
}
DEFAULT_PARAMS = {"length": 14, "upper": 60.0, "lower": 40.0}


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
    r = _rsi(bars_df["close"], int(p["length"]))
    r1 = r.shift(1)
    u, lw = float(p["upper"]), float(p["lower"])
    le = (r1 < u) & (r >= u)
    lx = (r1 > u) & (r <= u)
    se = (r1 > lw) & (r <= lw)
    sx = (r1 < lw) & (r >= lw)
    # a close after the opposite entry on the same bar leaves the reversal
    return le, lx & ~se, se & ~le, sx & ~le


def portfolio_kwargs(**params):
    return {}
