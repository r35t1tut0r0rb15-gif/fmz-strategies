"""ADX direction with an activity floor, 1-hour bars, long only: the ADX above 15 with +DI above -DI goes long; the ADX above 15 with -DI above +DI closes.
Port of FMZ strategy #443106 "Momentum Average Directional Movement Index Moving Average Crossover Strategy" (MA ADX Strategy).

FMZ source id: 443106

Source
    https://www.fmz.com/strategy/443106 (PineScript v5, FMZ last modified 2024-02-29 11:50:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-165), DI 14, ADX smoothing 14, ADX active 15; WMA 50 (colour only); percent of equity; dates (all)
    trueRangeSmoothed = rma(atr(14), 14);  +DI / -DI = fixnan(100 rma(DM, 14) / trueRangeSmoothed);  ADX = 100 rma(|+DI - -DI| / max(sum, 1), 14)
    ADX > 15 and +DI > -DI -> entry Buy;  ADX > 15 and +DI < -DI -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The true range is smoothed twice (rma of the ATR), and the ADX divides by max(sum, 1), as written.
      The WMA only colours. Long only. The percent-of-equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX direction with a floor.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_443106_adx15_di_direction_long"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "di_length": [14, 7],
    "adx_active": [15, 25],
}
DEFAULT_PARAMS = {"di_length": 14, "adx_active": 15, "adx_smoothing": 14}


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


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["di_length"])
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trs = _rma(_rma(tr, n), n)
    plus = _fixnan(100 * _rma(pdm, n) / trs)
    minus = _fixnan(100 * _rma(mdm, n) / trs)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / np.maximum(s, 1), int(p["adx_smoothing"]))
    act = float(p["adx_active"])
    le = (adx > act) & (plus > minus)
    lx = (adx > act) & (plus < minus)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
