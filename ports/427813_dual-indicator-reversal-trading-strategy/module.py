"""HPotter combo, 3-hour bars: the 123 reversal (two closes turning with the stochastic 14 crossing its
3-bar average beyond 50) and a CCI 10 fast/slow average cross must agree; long when both say long,
short when both say short, flat otherwise.
Port of FMZ strategy #427813 "Dual Indicator Reversal Trading Strategy" (Combo 123 Reversal & CCI).

FMZ source id: 427813

Source
    https://www.fmz.com/strategy/427813 (PineScript v4, FMZ last modified 2023-09-25 17:46:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 245-282), stoch 14 / K 1 / D 3 / level 50, CCI 10 with SMAs 10 / 20
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else hold
    CCI: sma(cci, 20) < sma(cci, 10) -> 1; > -> -1; else hold
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" (default false) is fixed off.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432231, Jaccard 0.663); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427813_combo_123_reversal_cci"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "fast_ma": [10, 5],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50,
                  "cci_len": 10, "fast_ma": 10, "slow_ma": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(x, n):
    """ta.cci: (x - sma) / (0.015 * mean absolute deviation)."""
    ma = x.rolling(n).mean()
    mad = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * mad)


def _hold(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    pos = 0
    for i in range(len(up)):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        out[i] = pos
    return out


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lv = p["level"]
    r_up = ((c2 < c1) & (c > c1) & (k < d) & (k > lv)).to_numpy()
    r_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < lv)).to_numpy()
    cci = _cci(c, int(p["cci_len"]))
    slow, fast = cci.rolling(int(p["slow_ma"])).mean(), cci.rolling(int(p["fast_ma"])).mean()
    c_up, c_dn = (slow < fast).to_numpy(), (slow > fast).to_numpy()
    a, b = _hold(r_up, r_dn), _hold(c_up, c_dn)
    tgt = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
