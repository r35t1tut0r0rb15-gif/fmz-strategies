"""MAHL band entries: long when the open sits below a low-anchored level of the 3-bar MA of lows
while DI+ led DI- and the band midpoint was rising on the previous bar; short mirror (always in).
Port of FMZ strategy #362497 "MAHL-Band".

Source
    https://www.fmz.com/strategy/362497 (PineScript v5, FMZ last modified 2022-05-11 20:48:53).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 40-67), MA length 3, DMI(17, 14)
    mahv = sma(high,3); malv = sma(low,3); mamv = (mahv + malv)/2
    up   = open < (malv - low/3 + open/3) and diplus[1] > diminus[1] and mamv[1] > mamv[2]
    down = open > (mahv - high/3 + open/3) and diplus[1] < diminus[1] and mamv[1] < mamv[2]
    up -> entry long;  else down -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The open/low/high combination compares prices of the same instrument, so it is scale-free.
    * ta.dmi(17, 14): DI length 17 (RMA), as Pine's dirmov.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362497_mahl_band_dmi_entry"
FAMILY = "directional_movement"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [3, 5, 8],
    "di_len": [14, 17, 21],
}
DEFAULT_PARAMS = {"ma_len": 3, "di_len": 17, "adx_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    n = int(p["ma_len"])
    mah, mal = h.rolling(n).mean(), lo.rolling(n).mean()
    mam = (mah + mal) / 2
    dip, dim, _ = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    up = ((o < mal - lo / 3 + o / 3) & (dip.shift(1) > dim.shift(1)) & (mam.shift(1) > mam.shift(2))).to_numpy()
    dn = ((o > mah - h / 3 + o / 3) & (dip.shift(1) < dim.shift(1)) & (mam.shift(1) < mam.shift(2))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
