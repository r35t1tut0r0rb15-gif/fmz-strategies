"""RSI 14 crossing under 30 buys, 1-hour bars, long only: a later close under 98.5 % of the latest signal close closes.
Port of FMZ strategy #446458 "RSI止损追踪交易策略-RSI-Stop-Loss-Tracking-Trading-Strategy" (RSI Trading Bot).

FMZ source id: 446458

Source
    https://www.fmz.com/strategy/446458 (PineScript v5, FMZ last modified 2024-03-28 17:56:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-139), RSI 14, threshold 30; stop 1.5 % of the signal close (bar-close test)
    crossunder(rsi, 30) -> entry Long, positionOpen, stopLossPrice = close x 0.985;  positionOpen and close < stopLossPrice -> close Long, positionOpen off

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a bar-close test, not an order: the close is compared with 98.5 % of the signal
      bar's close and strategy.close fills at the next open. A new signal while long re-bases the level
      on its own close, as written (the port follows it; the repeated entry itself is ignored). The
      only exit is that test. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is a close test at the bar close.
    2 generic: PASS, RSI cross-down with a close-based stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_446458_rsi14_cross_under_30_close_stop_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [30, 25],
    "stop_pct": [1.5, 3.0],
}
DEFAULT_PARAMS = {"threshold": 30.0, "stop_pct": 1.5, "rsi_len": 14}


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
    r = _rsi(c, int(p["rsi_len"]))
    th = float(p["threshold"])
    go = ((r < th) & (r.shift(1) >= th)).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = 1.0 - float(p["stop_pct"]) / 100.0
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag, lvl = False, np.nan
    for i in range(m):
        if go[i]:
            if not flag:
                le[i] = True
            flag, lvl = True, cv[i] * k
        if flag and cv[i] < lvl:
            lx[i] = True
            flag, lvl = False, np.nan
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
