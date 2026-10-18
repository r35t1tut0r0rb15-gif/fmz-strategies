"""Three simple averages, 1-hour bars, long only: the SMA 50 crossing over the SMA 100, the SMA 50 over the SMA 200 or the SMA 100 over the SMA 200 opens
a long (one trade at a time); each trade is closed by the opposite crossing of its own pair.
Port of FMZ strategy #435959 "Multiple Moving Averages Crossover Trading Strategy" (Triple Many Moving Averages (ST9 - Long Market Only)).

FMZ source id: 435959

Source
    https://www.fmz.com/strategy/435959 (PineScript v4, FMZ last modified 2023-12-20 14:12:20).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 157-434), SMA 50 / 100 / 200 on the current resolution; all three cross sets traded; forecasts, ribbons and labels only draw
    12: crossover(ma1, ma2) -> entry "1 over 2", crossunder -> close "1 over 2";  13: crossover(ma1, ma3) -> entry "1 over 3", crossunder -> close;  23: crossover(ma2, ma3) -> entry "2 over 3", crossunder -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 1 lets one long stand: an entry while a trade is open does nothing, and
      strategy.close(id) closes only the trade with that id (a trade opened by the 50 / 200 cross
      is not closed by the 50 / 100 cross under). The six orders of one bar are filled in the script's
      call order at the next open. The resolutions are "00 Current" (request.security at the chart
      resolution returns the chart's values); the VWMA option would read volume and is not used. The
      forecast and ribbon series are only plotted. The percent-of-equity size is sizing. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430849 (2 members, best partner #430849, Jaccard 0.757); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435959_triple_sma_cross_ids_long"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [50, 20],
    "ma2": [100, 50],
}
DEFAULT_PARAMS = {"ma1": 50, "ma2": 100, "ma3": 200}


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


def _xo(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False).to_numpy()


def _xu(a, b):
    return ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    m1, m2, m3 = (c.rolling(int(p[k])).mean() for k in ("ma1", "ma2", "ma3"))
    o12, u12 = _xo(m1, m2), _xu(m1, m2)
    o13, u13 = _xo(m1, m3), _xu(m1, m3)
    o23, u23 = _xo(m2, m3), _xu(m2, m3)
    n = len(o12)
    held = np.zeros(n, dtype=np.int8)
    tag = 0                                    # 0 flat, else the id of the open long trade (1, 2 or 3)
    pend = None
    for i in range(n):
        if i > 0 and pend is not None:
            e1, c1, e2, c2, e3, c3 = pend
            if e1 and tag == 0:
                tag = 1
            if c1 and tag == 1:
                tag = 0
            if e2 and tag == 0:
                tag = 2
            if c2 and tag == 2:
                tag = 0
            if e3 and tag == 0:
                tag = 3
            if c3 and tag == 3:
                tag = 0
        held[i] = 1 if tag else 0
        pend = (o12[i], u12[i], o13[i], u13[i], o23[i], u23[i])
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
