"""HPotter Williams A/D against its SMA 14, 1-hour bars: the A/D line above its average goes long, below goes short; held in
between and reversed on the opposite side. The line adds close - previous low on an up close, close - previous high on a
down close, and resets to 0 on an unchanged close, as written.
Port of FMZ strategy #434609 "移动平均聚合Williams商业区买卖压力指标策略Moving-Average-Aggregation-Williams-Commercial-Bid-Ask-Pressure-Indicator-Strategy" (Smoothened Williams Accumulation/Distribution (Williams AD)).

FMZ source id: 434609

Source
    https://www.fmz.com/strategy/434609 (PineScript v2, FMZ last modified 2023-12-07 17:48:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 134-149), length 14, reverse false
    WAD = close > close[1] ? WAD[1] + close - low[1] : close < close[1] ? WAD[1] + close - high[1] : 0
    pos = WAD > sma(WAD, 14) ? 1 : WAD < sma ? -1 : pos[1];  1 -> entry long;  -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script uses the previous bar's low / high (not Williams' true-range low / high) and the
      else branch is 0 (a reset), as written. strategy.entry reverses: REVERSAL INTENDED. reverse is
      false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a price-change accumulation against its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430903 (2 members, best partner #430903, Jaccard 0.792); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434609_williams_ad_sma_side"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 30],
    "reverse": [False, True],
}
DEFAULT_PARAMS = {"length": 14, "reverse": False}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    wad = np.zeros(m)
    for i in range(m):
        cp = c[i - 1] if i > 0 else 0.0           # nz(close[1], 0)
        w1 = wad[i - 1] if i > 0 else 0.0
        if c[i] > cp:
            wad[i] = w1 + c[i] - (lo[i - 1] if i > 0 else np.nan)
        elif c[i] < cp:
            wad[i] = w1 + c[i] - (h[i - 1] if i > 0 else np.nan)
        else:
            wad[i] = 0.0
        if np.isnan(wad[i]):
            wad[i] = 0.0 if i == 0 else wad[i]
    ws = pd.Series(wad, index=bars_df.index)
    ma = ws.rolling(int(p["length"])).mean()
    up, dn = (ws > ma).to_numpy(), (ws < ma).to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    if bool(p["reverse"]):
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
