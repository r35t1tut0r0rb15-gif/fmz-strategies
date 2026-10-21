"""Two Hull-style moving averages against their 2-bar-lagged copies with MACD and TSI filters, 1-hour bars: from flat, both Hull pairs up with the MACD above its signal, the faster Hull under the close and the
smoothed TSI above -4 goes long; the mirror goes short; both Hull pairs down with the faster Hull above the close closes a long, the mirror closes a short.
Port of FMZ strategy #438033 "多重交叉海龟与加权移动平均线与MACD与TSI组合策略Multiple-Crossovers-Turtle-and-Weighted-Moving-Average-and-MACD-and-TSI-Combination-Strategy" (MultiCross).

FMZ source id: 438033

Source
    https://www.fmz.com/strategy/438033 (PineScript v2, FMZ last modified 2024-01-08 14:19:02).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 222-279), Hull 7 / 14; VWMA 1; MACD 7 / 14 / 3; TSI 5 / 3, signal 2, lines +4 / -4
    n1 = wma(2 wma(close, 4) - wma(close, 7), 3), n2 = the same of close[2];  n3 / n4 the same with 14 (7, 4);  meh1 = vwma(close, 1)
    closelong = n1 < n2 and n3 < n4 and n1 > meh1;  closeshort = n1 > n2 and n3 > n4 and n1 < meh1
    long = opentrades < 1 and n1 > n2 and MACD > aMACD and n1 < meh1 and n3 > n4 and ema(tsi, 2) > -4;  short = opentrades < 1 and n1 < n2 and MACD < aMACD and n1 > meh1 and n3 < n4 and ema(tsi, 2) < 4

Interpretation choices (Pine rules in SURVEY_README.md)
    * vwma(close, 1) is the close itself (the volume cancels over one bar). Pine's round is half away from
      zero (7 / 2 -> 4). The closes act on the position held at the bar close and the entries need no
      open trade at the bar close, so a closing bar cannot also enter. Entries only from flat: Opposite
      entries cannot occur. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull-style averages, MACD and TSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG438033 (2 members, best partner #435834, Jaccard 0.949); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438033_quad_hull_macd_tsi_multicross"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [7, 14],
    "teh": [14, 28],
}
DEFAULT_PARAMS = {"keh": 7, "teh": 14, "fast": 7, "slow": 14, "macd_len": 3, "tsi_long": 5, "tsi_short": 3,
                  "tsi_signal": 2, "linebuy": 4.0, "linesell": -4.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pine_round(x):
    return int(np.floor(x + 0.5))


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hull_pair(c, k):
    h2, sq = max(1, _pine_round(k / 2)), max(1, _pine_round(np.sqrt(k)))
    a = _wma(2 * _wma(c, h2) - _wma(c, k), sq)
    c2 = c.shift(2)
    b = _wma(2 * _wma(c2, h2) - _wma(c2, k), sq)
    return a, b


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n1, n2 = _hull_pair(c, int(p["keh"]))
    n3, n4 = _hull_pair(c, int(p["teh"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    amacd = macd.ewm(span=int(p["macd_len"]), adjust=False).mean()
    pc = c.diff()
    a, b = int(p["tsi_long"]), int(p["tsi_short"])
    ds = pc.ewm(span=a, adjust=False).mean().ewm(span=b, adjust=False).mean()
    dsa = pc.abs().ewm(span=a, adjust=False).mean().ewm(span=b, adjust=False).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        tsi = 100.0 * ds / dsa
    ts = tsi.ewm(span=int(p["tsi_signal"]), adjust=False).mean()
    cl = ((n1 < n2) & (n3 < n4) & (n1 > c)).to_numpy()
    cs = ((n1 > n2) & (n3 > n4) & (n1 < c)).to_numpy()
    lc = ((n1 > n2) & (macd > amacd) & (n1 < c) & (n3 > n4) & (ts > float(p["linesell"]))).to_numpy()
    sc = ((n1 < n2) & (macd < amacd) & (n1 > c) & (n3 < n4) & (ts < float(p["linebuy"]))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1:
            if cl[i]:
                lx[i], pos = True, 0
        elif pos == -1:
            if cs[i]:
                sx[i], pos = True, 0
        elif i + 1 < m:
            if lc[i]:
                le[i], pos = True, 1
            elif sc[i]:
                se[i], pos = True, -1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
