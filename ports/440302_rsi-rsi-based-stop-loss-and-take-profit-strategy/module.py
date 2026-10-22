"""RSI 14 crossings, 1-hour bars: the RSI crossing over 35 goes long, crossing under 65 goes short; reversing (the stop and target levels are computed but no exit order is written).
Port of FMZ strategy #440302 "基于RSI的止损止盈策略RSI-based-Stop-Loss-and-Take-Profit-Strategy" (twelve12 first RSI remix).

FMZ source id: 440302

Source
    https://www.fmz.com/strategy/440302 (PineScript v5, FMZ last modified 2024-01-29 10:30:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-143), RSI 14; oversold 35, overbought 65; stop 5 %, target 10 % (levels only)
    co = crossover(rsi, 35) -> entry RsiLE;  cu = crossunder(rsi, 65) -> entry RsiSE;  longStopLoss / longTakeProfit / shortStopLoss / shortTakeProfit = avg price x (1 -/+ 5 % / 10 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script ends after computing the four levels (the comment announcing the exits has no code
      under it), so no exit order is placed and the levels are not ported. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI crossings.
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

NAME = "fmz_440302_rsi14_35_65_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "oversold": [35, 25],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 35}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))
    os_ = float(p["oversold"])
    ob = 100 - os_
    up = (r > os_) & (r.shift(1) <= os_)
    dn = (r < ob) & (r.shift(1) >= ob)
    false = pd.Series(False, index=c.index)
    return up & ~dn, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
