"""123 reversal and Vervoort ATR trailing-stop combo, 1-hour bars: long when the 123 state and the 3.5 x ATR(5) trailing-line state are both up, short when both are down, flat when they disagree.
Port of FMZ strategy #440062 "双均线反转与ATR-trailing-stop组合策略Combination-Strategy-of-Dual-Moving-Average-Reversal-and-ATR-Trailing-Stop" (Combo Backtest 123 Reversal & Average True Range Trailing Stops).

FMZ source id: 440062

Source
    https://www.fmz.com/strategy/440062 (PineScript v3, FMZ last modified 2024-01-26 11:26:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-238), 123: 14 / 1 / 3 / 50; ATR trailing stop 5 x 3.5; reverse off
    xATRTrailingStop ratchets close -/+ 3.5 atr(5) (nz history);  ATR pos = close crossing the previous line up 1 / down -1, else previous
    both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line starts from zero history (nz), as written. The 123 test is read as written. The
      states are levels; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and an ATR trailing line.
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

NAME = "fmz_440062_reversal123_atr_trailing_stop_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "n_atr_multip": [3.5, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "n_atr_multip": 3.5, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "n_atr_period": 5, "reverse": False}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    loss = (float(p["n_atr_multip"]) * _atr(bars_df, p["n_atr_period"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    ts_prev, pa, p123 = 0.0, 0, 0
    for i in range(m):
        cp = cv[i - 1] if i > 0 else np.nan
        if cv[i] > ts_prev and cp > ts_prev:
            ts = max(ts_prev, cv[i] - loss[i])
        elif cv[i] < ts_prev and cp < ts_prev:
            ts = min(ts_prev, cv[i] + loss[i])
        elif cv[i] > ts_prev:
            ts = cv[i] - loss[i]
        else:
            ts = cv[i] + loss[i]
        if cp < ts_prev and cv[i] > ts_prev:
            pa = 1
        elif cp > ts_prev and cv[i] < ts_prev:
            pa = -1
        ts_prev = ts if not np.isnan(ts) else 0.0
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        tgt[i] = 1 if (p123 == 1 and pa == 1) else (-1 if (p123 == -1 and pa == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
