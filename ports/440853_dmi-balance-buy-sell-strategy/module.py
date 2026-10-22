"""DMI crossings, bar size pending, long only: +DI crossing over -DI on the same bar as it crosses over the ADX (14 / 14) goes long; +DI crossing under -DI or under the ADX closes.
Port of FMZ strategy #440853 "DMI Balance Buy Sell Strategy" (DMI Buy/Sell Strategy).

FMZ source id: 440853

Source
    https://www.fmz.com/strategy/440853 (PineScript v5, FMZ last modified 2024-02-02 17:07:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-161), DMI length 14, ADX smoothing 14; no backtest header
    [diPlus, diMinus, adx] = ta.dmi(14, 14);  buy = crossover(diPlus, diMinus) and crossover(diPlus, adx) -> entry Buy;  sell = crossunder(diPlus, diMinus) or crossunder(diPlus, adx) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.dmi uses Wilder smoothing (rma) of the true range and the directional moves. The buy and
      sell tests cannot hold together. The source has no backtest header and names no bar size: FREQ =
      "bar_size_pending" (rule 1); precompute builds the bars with the house
      bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies bar_size (never in GRID /
      DEFAULT_PARAMS). Long only. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, DMI crossings.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_440853_dmi_double_cross_long"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "adx_smoothing": [14, 7],
}
DEFAULT_PARAMS = {"length": 14, "adx_smoothing": 14}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def _dmi(bars_df, n, m_):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trr = _rma(tr, n)
    plus = 100 * _rma(pdm, n) / trr
    minus = 100 * _rma(mdm, n) / trr
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), m_)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pl, mi, adx = _dmi(bars_df, int(p["length"]), int(p["adx_smoothing"]))

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    buy = xo(pl, mi) & xo(pl, adx)
    sell = xo(mi, pl) | xo(adx, pl)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell & ~buy, false, false.copy()


def portfolio_kwargs(**params):
    return {}
