"""HPotter DMI + MA, 3-hour bars: +DI crossing above -DI on the same bar as the close crossing above
SMA 30 goes long; both crossing down goes short; otherwise the last side is kept.
Port of FMZ strategy #428075 "Combining DMI and Moving Average Trading Strategy".

FMZ source id: 428075

Source
    https://www.fmz.com/strategy/428075 (PineScript v2, FMZ last modified 2023-09-28 12:39:44).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 159-198), SMA 30, DMI 14
    +DI / -DI = fixnan(100 rma(+DM / -DM, 14) / rma(tr, 14))
    long = +DI crosses above -DI and close crosses above sma30 (same bar) -> 1; mirror -> -1; else hold
    -> entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" (default false) fixed off. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA and DMI lengths only.
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

NAME = "fmz_428075_hpotter_dmi_ma_cross"
FAMILY = "dmi_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ma": [30, 50],
    "length_dmi": [14, 7],
}
DEFAULT_PARAMS = {"length_ma": 30, "length_dmi": 14}


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


def _fixnan(x):
    """Pine fixnan: an na value takes the last non-na value of the same series (past only)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["length_ma"])).mean()
    up, dn = h.diff(), -lo.diff()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    n = int(p["length_dmi"])
    trur = _rma(tr, n)
    pdi = _fixnan(100 * _rma(up.where((up > dn) & (up > 0), 0.0), n) / trur)
    ndi = _fixnan(100 * _rma(dn.where((dn > up) & (dn > 0), 0.0), n) / trur)
    di_up = (pdi > ndi) & (pdi.shift(1) < ndi.shift(1))
    di_dn = (pdi < ndi) & (pdi.shift(1) > ndi.shift(1))
    ma_up = (c > ma) & (c.shift(1) < ma.shift(1))
    ma_dn = (c < ma) & (c.shift(1) > ma.shift(1))
    long_s, short_s = (di_up & ma_up).to_numpy(), (di_dn & ma_dn).to_numpy()
    m = len(long_s)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_s[i]:
            pos = 1
        elif short_s[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
