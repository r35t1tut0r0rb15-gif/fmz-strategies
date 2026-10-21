"""Stiffness index levels, 3-minute bars: the EMA 3 of the share of the last 60 closes above (SMA 100 - 0.2 sigma) crossing over 90 goes long, a falling value above 90 closes it; crossing under 90, or a falling value
under 90, goes short, a rising value under 90 closes it.
Port of FMZ strategy #437494 "Stiffness Breakthrough Strategy" (Stiffness Strategy).

FMZ source id: 437494

Source
    https://www.fmz.com/strategy/437494 (PineScript v4, FMZ last modified 2024-01-03 11:34:34).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 149-170), MA 100, stiffness 60, smoothing 3, threshold 90
    bound = sma(close, 100) - 0.2 stdev(close, 100);  stiffness = ema(sum(close > bound, 60) x 100 / 60, 3)
    long = crossover(stiffness, 90);  close long = stiffness > 90 and falling(1);  short = crossunder(stiffness, 90) or (stiffness < 90 and falling(1));  close short = stiffness < 90 and rising(1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev is the population deviation; falling / rising(x, 1) compare with the previous value. Orders follow
      the script's call order (entry long, close long, entry short, close short); a close only acts on the
      position open at the bar's close and left unchanged by the entries. REVERSAL INTENDED. The 100 % of
      equity size and commission are sizing. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, share-of-bars index levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_437494_stiffness_threshold"
FAMILY = "momentum_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [100, 50],
    "stiff_length": [60, 30],
}
DEFAULT_PARAMS = {"ma_length": 100, "stiff_length": 60, "stiff_smooth": 3, "threshold": 90.0}


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


def _call_order(lc, lxc, sc, sxc):
    """Pine call order: entry long, close long, entry short, close short (closes act on the calc-time position)."""
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s, changed = pos, False
        if lc[i] and s != 1:
            s, changed = 1, True
        if lxc[i] and pos == 1 and not changed:
            s = 0
        if sc[i] and s != -1:
            s, changed = -1, True
        if sxc[i] and pos == -1 and not changed:
            s = 0
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        elif s == 0 and pos == 1:
            lx[i] = True
        elif s == 0 and pos == -1:
            sx[i] = True
        pos = s
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["ma_length"])
    bound = c.rolling(n).mean() - 0.2 * c.rolling(n).std(ddof=0)
    k = int(p["stiff_length"])
    above = (c > bound).astype(float).rolling(k).sum()
    st = (above * 100 / k).ewm(span=int(p["stiff_smooth"]), adjust=False).mean()
    st1 = st.shift(1)
    th = float(p["threshold"])
    lc = ((st > th) & (st1 <= th)).to_numpy()
    lxc = ((st > th) & (st < st1)).to_numpy()
    sc = (((st < th) & (st1 >= th)) | ((st < th) & (st < st1))).to_numpy()
    sxc = ((st < th) & (st > st1)).to_numpy()
    le, lx, se, sx = _call_order(lc, lxc, sc, sxc)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
