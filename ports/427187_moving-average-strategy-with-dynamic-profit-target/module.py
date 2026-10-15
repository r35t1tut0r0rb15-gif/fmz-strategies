"""SMA 80 turn with an ATR profit target: the SMA turning up (after falling) goes long, turning down
goes short, each only if the last signal was not already that side; an open position takes profit
12 x ATR(252) beyond the close.
Port of FMZ strategy #427187 "Moving Average Strategy with Dynamic Profit Target".

FMZ source id: 427187

Source
    https://www.fmz.com/strategy/427187 (PineScript v4, FMZ last modified 2023-09-18 21:46:47).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 149-197), SMA 80, target ATR 252 x 12
    trend = sma(close, 80)
    signal != 1 and trend[1] < trend[2] and trend > trend[1] -> entry long, signal = 1
    signal != -1 and trend[1] > trend[2] and trend < trend[1] -> entry short, signal = -1
    long: exit(limit = close + 12 atr(252)); short: exit(limit = close - 12 atr(252)), re-issued every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * `signal` remembers the last ENTRY side, not the position: after a take-profit the same side
      cannot re-enter until the other side has signalled (as written).
    * The target is re-issued at every bar's close (a level that moves after entry): it cannot be
      expressed by stops() (the house trail is a stop, not a moving target): rule 2, mark
      trailing_stop_pending. The port fixes the target at entry: tp_stop = 12 x ATR(252) / close
      of the signal bar, shifted one bar inside stops() (known at the fill bar's open).
    * The ATR-based lot (investment / ATR x 0.1) is computed but never passed to an order.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}: stop module, driver D4).
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving target is fixed at entry (marked).
    2 generic: PASS, MA length and an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the unused lot formula is stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427187_sma_turn_atr_target"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [80, 40, 160],
    "pt_factor": [12.0, 6.0],
}
DEFAULT_PARAMS = {"period": 80, "pt_period": 252, "pt_factor": 12.0}


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = bars_df["close"].rolling(int(p["period"])).mean()
    t1, t2 = t.shift(1).fillna(0.0), t.shift(2).fillna(0.0)   # nz()
    up = ((t1 < t2) & (t > t1)).to_numpy()
    dn = ((t1 > t2) & (t < t1)).to_numpy()
    m = len(t)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    signal = 0
    for i in range(m):
        if signal != 1 and up[i]:
            le[i], signal = True, 1
        elif signal != -1 and dn[i]:
            se[i], signal = True, -1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dist = p["pt_factor"] * _atr(bars_df, int(p["pt_period"])) / bars_df["close"]
    return {"tp_stop": dist.shift(1)}


def portfolio_kwargs(**params):
    return {}
