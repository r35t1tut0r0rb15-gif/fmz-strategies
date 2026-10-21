"""Hull average 5 / 7 crossings with turning-point exits, 1-hour bars: the first HMA crossing over the second goes long, under goes short (reversing); the first HMA's 1-bar rate of change crossing over +0.02 %
flags it "up", crossing under -0.02 % flags it "down"; a flip from down to up closes a short, from up to down closes a long.
Port of FMZ strategy #436860 "Reversal Dual Moving Average Crossover Strategy" (MA Crossover Strategy with MA Turning Point Exits).

FMZ source id: 436860

Source
    https://www.fmz.com/strategy/436860 (PineScript v3, FMZ last modified 2023-12-28 12:00:27).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 71-146), MA 1: HMA 5, MA 2: HMA 7, look back 1, minimum slope 2 x 0.01 (percent)
    price1 / price2 = HMA(close, 5 / 7) (types SMA, EMA, HMA, VWMA);  crossover(price1, price2) -> entry Long;  crossunder -> entry Short
    roc1 = roc(price1, 1);  crossover(roc1, 0.02) -> ma1up;  crossunder(roc1, -0.02) -> ma1down;  ma1up and ma1down[1] -> close Short;  ma1down and ma1up[1] -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * HMA(n) = wma(2 wma(src, n / 2) - wma(src, n), round(sqrt(n))) with Pine v3 integer division (5 / 2
      = 2). The roc is in percent, so the 0.02 threshold is dimensionless. The VWMA option needs volume and
      is left out (check 8; not the default). The same-resolution security() is the chart's own close.
      Orders follow the script's call order: the entries first, then the closes, which only close a
      position open at the bar's close. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossing and percent slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430020 (4 members, best partner #440310, Jaccard 0.768); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436860_hma_cross_turning_point_exit"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [5, 9],
    "ma2": [7, 14],
}
DEFAULT_PARAMS = {"ma1": 5, "ma2": 7, "type1": "HMA", "type2": "HMA", "lookback1": 1, "slope": 2.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _ma(src, n, kind):
    if kind == "SMA":
        return src.rolling(n).mean()
    if kind == "EMA":
        return src.ewm(span=n, adjust=False).mean()
    if kind == "HMA":
        return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))
    raise ValueError(f"MA type {kind!r} not ported (VWMA needs volume, check 8)")


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    p1 = _ma(c, int(p["ma1"]), p["type1"])
    p2 = _ma(c, int(p["ma2"]), p["type2"])
    lc = ((p1 > p2) & (p1.shift(1) <= p2.shift(1))).to_numpy()
    sc = ((p1 < p2) & (p1.shift(1) >= p2.shift(1))).to_numpy()
    k = int(p["lookback1"])
    roc = 100.0 * (p1 - p1.shift(k)) / p1.shift(k)
    t = float(p["slope"]) * 0.01
    r_up = ((roc > t) & (roc.shift(1) <= t)).to_numpy()
    r_dn = ((roc < -t) & (roc.shift(1) >= -t)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    up = dn = False
    pos = 0
    for i in range(m):
        up_prev, dn_prev = up, dn
        if r_up[i]:
            up, dn = True, False
        if r_dn[i]:
            up, dn = False, True
        sxc = up and dn_prev
        lxc = dn and up_prev
        new = pos
        if lc[i] and pos <= 0:
            new = 1
        elif sc[i] and pos >= 0:
            new = -1
        elif (lxc and pos == 1) or (sxc and pos == -1):
            new = 0
        if new == 1 and pos != 1:
            le[i] = True
        elif new == -1 and pos != -1:
            se[i] = True
        elif new == 0 and pos == 1:
            lx[i] = True
        elif new == 0 and pos == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
