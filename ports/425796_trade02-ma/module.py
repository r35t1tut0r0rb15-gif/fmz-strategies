"""Aroon + long EMA (MyLanguage): an Aroon-up cross above 70 (or Aroon-down cross below 30) with
Aroon up above Aroon down and the close above EMA(240) reverses to long; the mirror reverses to
short. Aroon-up falling through 50 closes a long; Aroon-down falling through 50 closes a short.
Port of FMZ strategy #425796 "Trade02-阿隆指标MA策略".

Source
    https://www.fmz.com/strategy/425796 (MyLanguage, author 作手君TradeMan, FMZ last modified
    2023-09-04 22:33:13). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 47-77), N 240 (header args 120)
    MALONG = EMA(REF(C,1), N)
    HH_N = MIN(BARSLAST(HHV(H,N) > HHV(REF(H,1),N)) + 1, N);  LL_N mirrors with lows
    AROON_UP = (N - HH_N) / N * 100;  AROON_DN likewise;  AROON = UP - DN
    (CROSSUP(UP,70) or CROSSDOWN(DN,30)) and AROON > 0 and BKVOL <= 0 and C > MALONG -> BPK
    (CROSSUP(DN,70) or CROSSDOWN(UP,30)) and AROON < 0 and SKVOL <= 0 and C < MALONG -> SPK
    AROON > 0 and CROSSDOWN(UP,50) -> SP;  AROON < 0 and CROSSDOWN(DN,50) -> BP

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model: statements run in order on the completed bar; the port tracks the
      position through them and emits the net change of the bar (an open and a close of the
      same side on one bar net to no long).
    * BARSLAST of a condition never true is na, so the Aroon values are na until a new N-bar high
      / low has occurred, as coded. BPK / SPK reverse: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header. LOTS (MONEYTOT formula) -> original_sizing.txt.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_425796_aroon_ema_reversal"
FAMILY = "directional_movement"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "N": [60, 120, 240],
}
DEFAULT_PARAMS = {"N": 240}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _barslast(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["N"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.shift(1).ewm(span=n, adjust=False).mean().to_numpy()
    new_hi = (h.rolling(n).max() > h.shift(1).rolling(n).max()).to_numpy()
    new_lo = (l.rolling(n).min() < l.shift(1).rolling(n).min()).to_numpy()
    up = (n - np.minimum(_barslast(new_hi) + 1, n)) / n * 100
    dn = (n - np.minimum(_barslast(new_lo) + 1, n)) / n * 100
    ar = up - dn
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    xu = lambda a, v: (a > v) & (lag(a) <= v)
    xd = lambda a, v: (a < v) & (lag(a) >= v)
    cv = c.to_numpy(dtype=float)
    d_open = (xu(up, 70) | xd(dn, 30)) & (ar > 0) & (cv > ma)
    k_open = (xu(dn, 70) | xd(up, 30)) & (ar < 0) & (cv < ma)
    pd_close = (ar > 0) & xd(up, 50)
    pk_close = (ar < 0) & xd(dn, 50)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        before = pos
        if d_open[i] and pos != 1:
            pos = 1
        if k_open[i] and pos != -1:
            pos = -1
        if pd_close[i] and pos == 1:
            pos = 0
        if pk_close[i] and pos == -1:
            pos = 0
        if pos != before:
            if pos == 1:
                le[i] = True
            elif pos == -1:
                se[i] = True
            elif before == 1:
                lx[i] = True
            else:
                sx[i] = True
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
