"""Donchian midline crosses with swing exits, 30-minute bars: a close crossing above the midline of the previous 20 closes'
channel goes long, closed when a close falls under the 3-bar low (bars 1-3 back) less a third of the previous ATR 20; a
close crossing below the midline goes short, closed when a close rises over the 3-bar high plus a third of the ATR.
Port of FMZ strategy #434585 "Donchian Channel With Trailing Stop Loss Strategy" (dc).

FMZ source id: 434585

Source
    https://www.fmz.com/strategy/434585 (PineScript v4, FMZ last modified 2023-12-07 16:53:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-174), channel 20 on closes, [1]; ATR 20; date inputs unused (testPeriod() is always true)
    avg = (highest(close, 20)[1] + lowest(close, 20)[1]) / 2;  close > avg and cross(close, avg) -> entry long;  close < lowest(low[1], 3) - atr(20)[1] / 3 -> close long
    close < avg and cross(close, avg) -> entry short;  close > highest(high[1], 3) + atr(20)[1] / 3 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel uses closes up to the previous bar; the exit levels use the 3 bars before the
      current one and the previous bar's ATR. The closes act on the position held on the bar; an
      entry on the same bar wins (the short entry is issued last). strategy.entry reverses: REVERSAL
      INTENDED. The exits are close-based signals (no stop order). FREQ = "30min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midline crosses and ATR-padded swing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434585 (2 members, best partner #439076, Jaccard 0.872); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434585_donchian_mid_swing_exit"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 50],
    "atr_div": [3.0, 1.0],
}
DEFAULT_PARAMS = {"period": 20, "atr_len": 20, "swing": 3, "atr_div": 3.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["period"])
    avg = (c.rolling(n).max().shift(1) + c.rolling(n).min().shift(1)) / 2
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr1 = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().shift(1)
    k, d = int(p["swing"]), float(p["atr_div"])
    bstop = lo.shift(1).rolling(k).min() - atr1 / d
    sstop = h.shift(1).rolling(k).max() + atr1 / d
    crossed = ((c > avg) & (c1 <= avg.shift(1))) | ((c < avg) & (c1 >= avg.shift(1)))
    buy = ((c > avg) & crossed).to_numpy()
    sell = ((c < avg) & crossed).to_numpy()
    xl, xs = (c < bstop).to_numpy(), (c > sstop).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
