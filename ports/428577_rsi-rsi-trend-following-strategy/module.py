"""Pure RSI long only, hourly bars: RSI 14 crossing above 30 or above 55 goes long; the long closes when
RSI crosses back under 30, 55, 60 or 70, or rises above 75.
Port of FMZ strategy #428577 "RSI Trend Following Strategy" (Pure RSI long only).

FMZ source id: 428577

Source
    https://www.fmz.com/strategy/428577 (PineScript v4, FMZ last modified 2023-10-07 10:02:21).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-199), RSI 14, bands 30 / 55 / 60 / 70 / 75
    crossover(rsi, 30) or crossover(rsi, 55) -> entry long
    crossunder(rsi, 30 / 55 / 60 / 70) or rsi > 75 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * An entry and a close on one bar: the close acts only on an open position. Long only.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels only.
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

NAME = "fmz_428577_pure_rsi_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [14, 7],
    "rsi_top": [75, 80],
}
DEFAULT_PARAMS = {"rsi_period": 14, "rsi_low": 30, "rsi_middle": 55, "rsi_mhigh": 60, "rsi_high": 70, "rsi_top": 75}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    n = int(p["rsi_period"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    xo = lambda lv: (r > lv) & (r.shift(1) <= lv)
    xu = lambda lv: (r < lv) & (r.shift(1) >= lv)
    enter = (xo(p["rsi_low"]) | xo(p["rsi_middle"])).to_numpy()
    exit_ = (xu(p["rsi_low"]) | xu(p["rsi_middle"]) | xu(p["rsi_mhigh"]) | xu(p["rsi_high"])
             | (r > p["rsi_top"])).to_numpy()
    m = len(enter)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and exit_[i]:
            pos = 0
        if start == 0 and enter[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
