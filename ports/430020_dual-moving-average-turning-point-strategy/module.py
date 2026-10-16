"""MA turning point, 2-hour bars: the one-bar rate of change of an HMA 25 crossing above +0.025 % marks the average as
turning up, crossing below -0.025 % as turning down; the bar on which the state flips from down to up goes long, from
up to down goes short.
Port of FMZ strategy #430020 "Dual Moving Average Turning Point Strategy" (MA Turning Point Strategy).

FMZ source id: 430020

Source
    https://www.fmz.com/strategy/430020 (PineScript v3, FMZ last modified 2023-10-24 12:19:04).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 152-205), HMA 25 of close, lookback 1, minimum slope 2.5 x 0.01
    roc1 = roc(hma(close, 25), 1)                       (percent)
    crossover(roc1, 0.025)  -> ma1up := true,  ma1down := false
    crossunder(roc1, -0.025) -> ma1up := false, ma1down := true
    ma1up and ma1down[1] -> entry long;  ma1down and ma1up[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(syminfo.tickerid, timeframe.period, close) is the chart's own close.
    * "Minimum slope magnitude * 100" is multiplied by 0.01 and compared with ta.roc, which is in
      percent: the threshold is 0.025 %, as written. HMA half length int(25 / 2) = 12, root
      round(sqrt(25)) = 5.
    * The MA type options (SMA, EMA, VWMA) are not ported: the default HMA only (VWMA would use volume).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a percentage rate of change of a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND430020 (4 members, best partner #436860, Jaccard 0.754); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430020_hma_turning_point"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [25, 15, 40],
    "strength": [2.5, 5.0],
}
DEFAULT_PARAMS = {"ma_len": 25, "strength": 2.5, "lookback": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


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
    ma = _hma(bars_df["close"], int(p["ma_len"]))
    k = int(p["lookback"])
    roc = 100 * (ma - ma.shift(k)) / ma.shift(k)
    s = float(p["strength"]) * 0.01
    xu = ((roc > s) & (roc.shift(1) <= s)).to_numpy()
    xd = ((roc < -s) & (roc.shift(1) >= -s)).to_numpy()
    m = len(roc)
    tgt = np.zeros(m, dtype=np.int8)
    up = dn = False
    pos = 0
    for i in range(m):
        up1, dn1 = up, dn
        if xu[i]:
            up, dn = True, False
        if xd[i]:
            up, dn = False, True
        if up and dn1:
            pos = 1
        elif dn and up1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
