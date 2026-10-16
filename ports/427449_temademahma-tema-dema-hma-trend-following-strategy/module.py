"""TEMA / DEMA / HMA, no bar size of its own: DEMA 43 crossing under TEMA 8 while the Hull MA 52 is
rising goes long; DEMA crossing over TEMA while the Hull MA is falling goes short (each reverses the
other side).
Port of FMZ strategy #427449 "TEMA-DEMA-HMA Trend Following Strategy".

FMZ source id: 427449

Source
    https://www.fmz.com/strategy/427449 (PineScript v4, FMZ last modified 2023-09-21 10:56:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 121-167), TEMA 8, DEMA 43, Hull 52, rising test 2
    up = crossunder(dema, tema) and rising(hma, 2) -> entry long
    down = crossover(dema, tema) and falling(hma, 2) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md; skill section 5a)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with bar_sizes.build_bars(raw_1m_df, params["bar_size"]).
    * rising(x, 2) = x above each of its previous 2 values (falling mirrors), as Pine.
    * hma: wma(2 wma(close, n / 2) - wma(close, n), round(sqrt(n))), n / 2 rounded down.
    * strategy.entry reverses: REVERSAL INTENDED.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no.
    4 signals only: 100 % of equity, commission stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427449_tema_dema_hma"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "t_length": [8, 13],
    "d_length": [43, 21],
    "h_length": [52, 26],
}
DEFAULT_PARAMS = {"t_length": 8, "d_length": 43, "h_length": 52, "r_length": 2}


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nt, nd, nh, nr = (int(p[k]) for k in ("t_length", "d_length", "h_length", "r_length"))
    e1 = c.ewm(span=nt, adjust=False).mean()
    e2 = e1.ewm(span=nt, adjust=False).mean()
    tema = 3 * (e1 - e2) + e2.ewm(span=nt, adjust=False).mean()
    d1 = c.ewm(span=nd, adjust=False).mean()
    dema = 2 * d1 - d1.ewm(span=nd, adjust=False).mean()
    hma = _wma(2 * _wma(c, nh // 2) - _wma(c, nh), int(round(np.sqrt(nh))))
    prev_max = pd.concat([hma.shift(k) for k in range(1, nr + 1)], axis=1).max(axis=1, skipna=False)
    prev_min = pd.concat([hma.shift(k) for k in range(1, nr + 1)], axis=1).min(axis=1, skipna=False)
    rising, falling = hma > prev_max, hma < prev_min
    up = ((dema < tema) & (dema.shift(1) >= tema.shift(1)) & rising).to_numpy()
    dn = ((dema > tema) & (dema.shift(1) <= tema.shift(1)) & falling).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
