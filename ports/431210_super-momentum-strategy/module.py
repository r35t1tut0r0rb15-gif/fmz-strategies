"""Chande momentum crosses confirmed by five relative momentum indexes, 3-minute bars: the CMO (9, shifted +50) crossing
above 25 with RMI1-3 under their buy lines, RMI4 under 100 and RMI5 above 0 goes long; the CMO crossing below 75 with
RMI1-3 over their sell lines, RMI4 above 0 and RMI5 under 47 goes short.
Port of FMZ strategy #431210 "Super Momentum Strategy" (Super Momentum Strat).

FMZ source id: 431210

Source
    https://www.fmz.com/strategy/431210 (PineScript v4, FMZ last modified 2023-11-06 09:24:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 169-329), CMO 9 (25 / 75); RMI 8/3, 12/3, 30/53, 520/137, 520/137
    chandeMO = 100 (sum(up, 9) - sum(down, 9)) / (sum(up, 9) + sum(down, 9)) + 50
    rmiN = 100 - 100 / (1 + rma(max(change(close, mN), 0), lN) / rma(-min(change(close, mN), 0), lN)) (0 / 100 edge cases)
    long: rmi5 > 0 and rmi4 < 100 and rmi3 < 24 and rmi2 < 37 and rmi1 < 37 and crossover(chandeMO, 25) -> entry long
    short: rmi5 < 47 and rmi4 > 0 and rmi3 > 46 and rmi2 > 72 and rmi1 > 57 and crossunder(chandeMO, 75) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: RMI2 uses RMI1's momentum length (3) and tests up1 == 0 for its 0 case; RMI5 tests
      up4 == 0. rma is Wilder smoothing with an SMA seed (Pine). The time window is always true.
    * Entries only; strategy.entry reverses: REVERSAL INTENDED. FREQ = "3min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum oscillator levels.
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

NAME = "fmz_431210_super_momentum_cmo_rmi"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cmo_len": [9, 20],
    "cmo_buy": [25, 35],
}
DEFAULT_PARAMS = {"cmo_len": 9, "cmo_buy": 25}


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
    return out


def _updn(c, mom, n):
    ch = c - c.shift(mom)
    return _rma(ch.clip(lower=0), n), _rma((-ch).clip(lower=0), n)


def _rmi(up, dn, up_zero):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + up / dn)
    r = np.where(up_zero == 0, 0.0, r)
    r = np.where(dn == 0, 100.0, r)
    return np.where(np.isnan(up) | np.isnan(dn) | np.isnan(up_zero), np.nan, r)


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
    mom = c.diff()
    n = int(p["cmo_len"])
    s1, s2 = mom.clip(lower=0).rolling(n).sum(), (-mom).clip(lower=0).rolling(n).sum()
    cmo = (100 * (s1 - s2) / (s1 + s2) + 50).to_numpy()
    u1, d1 = _updn(c, 3, 8)
    u2, d2 = _updn(c, 3, 12)
    u3, d3 = _updn(c, 53, 30)
    u4, d4 = _updn(c, 137, 520)
    u5, d5 = u4, d4                                   # RMI5 has RMI4's lengths (520 / 137)
    r1, r2, r3 = _rmi(u1, d1, u1), _rmi(u2, d2, u1), _rmi(u3, d3, u3)
    r4, r5 = _rmi(u4, d4, u4), _rmi(u5, d5, u4)
    ob, os_ = 100 - float(p["cmo_buy"]), float(p["cmo_buy"])
    cmo1 = np.concatenate(([np.nan], cmo[:-1]))
    xo = (cmo > os_) & (cmo1 <= os_)
    xu = (cmo < ob) & (cmo1 >= ob)
    lg = (r5 > 0) & (r4 < 100) & (r3 < 24) & (r2 < 37) & (r1 < 37) & xo
    sh = (r5 < 47) & (r4 > 0) & (r3 > 46) & (r2 > 72) & (r1 > 57) & xu
    m = len(cmo)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lg[i]:
            pos = 1
        if sh[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
