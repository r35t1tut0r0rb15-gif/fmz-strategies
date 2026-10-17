"""HPotter T3-smoothed CCI, 30-minute bars: the CCI 14 smoothed by a six-stage T3 (period 5, b 0.618) above zero turns the
state long, below zero short; always in the state's direction.
Port of FMZ strategy #433075 "基于T3和CCI指标的趋势追踪策略T3-CCI-Trend-Tracking-Strategy" (FX Sniper: T3-CCI Strategy).

FMZ source id: 433075

Source
    https://www.fmz.com/strategy/433075 (PineScript v2, FMZ last modified 2023-11-24 10:33:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 156-190), CCI 14, T3 period 5, b 0.618, reverse false
    w1 = 2 / (nr + 1), nr = 1 + 0.5 (5 - 1);  e1..e6 = w1 x prev stage + w2 x nz(e[1]) (e1 on the CCI)
    xccir = c1 e6 + c2 e5 + c3 e4 + c4 e3 (T3 weights from b);  pos = xccir > 0 ? 1 : xccir < 0 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * cci() is (close - sma) / (0.015 x mean absolute deviation), 14 bars. The T3 stages start at 0
      (nz), as written. The state holds at exactly zero.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "30min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded-scale oscillator sign.
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

NAME = "fmz_433075_t3_cci_state"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [14, 28],
    "t3_len": [5, 10],
}
DEFAULT_PARAMS = {"cci_len": 14, "t3_len": 5, "b": 0.618}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        mu = win.mean(axis=1)
        md = np.abs(win - mu[:, None]).mean(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[n - 1:] = (v[n - 1:] - mu) / (0.015 * md)
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    x = _cci(bars_df["close"], int(p["cci_len"]))
    b = float(p["b"])
    b2, b3 = b * b, b * b * b
    k1, k2, k3, k4 = -b3, 3 * (b2 + b3), -3 * (2 * b2 + b + b3), 1 + 3 * b + b3 + 3 * b2
    nn = max(int(p["t3_len"]), 1)
    w1 = 2 / (1 + 0.5 * (nn - 1) + 1)
    w2 = 1 - w1
    m = len(x)
    e = [0.0] * 6
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        src = x[i]
        for j in range(6):
            prev_e = e[j] if not np.isnan(e[j]) else 0.0
            e[j] = w1 * src + w2 * prev_e
            src = e[j]
        r = k1 * e[5] + k2 * e[4] + k3 * e[3] + k4 * e[2]
        if r > 0:
            pos = 1
        elif r < 0:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
