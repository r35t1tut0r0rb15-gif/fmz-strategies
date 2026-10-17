"""EMA fan crosses, 1-hour bars, long only: from flat, any neighbouring pair of the EMAs 8 / 13 / 21 / 34 / 55 / 89 / 144 /
233 crossing up opens a long tied to that pair, closed when the same pair crosses back down. One position at a time.
Port of FMZ strategy #435101 "多个EMA周期动态交易策略Multi-Timeframe-Dynamic-EMA-Trading-Strategy" (EMA Fan).

FMZ source id: 435101

Source
    https://www.fmz.com/strategy/435101 (PineScript v2, FMZ last modified 2023-12-12 12:18:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 162-257), EMAs 8 / 13 / 21 / 34 / 55 / 89 / 144 / 233, all on; finish 2020-01-01
    crossover(ema_k, ema_k+1) -> entry "EMAk" (qty 1 / (close x 7));  time > finish or crossunder(ema_k, ema_k+1) -> close "EMAk"

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding is 1, so only the first pair's entry fills; each close names its own entry, so the
      port tracks which pair opened the trade (the lowest pair wins on a shared bar). An entry on the
      bar of an exit is not taken (the position is still open when the bar is calculated).
    * "time > finish" (finish = 2020) would close every trade on the bar after it opens on the
      project's data: the date window is the author's and is dropped, as with the other ports.
      The per-pair quantity is sizing. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exit follows the opening entry (tracked).
    2 generic: PASS, average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1 / (close x count) quantity stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435101_ema_fan_pair_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "first": [8, 5],
}
DEFAULT_PARAMS = {"first": 8}

FAN = (13, 21, 34, 55, 89, 144, 233)


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
    c = bars_df["close"]
    lens = (int(p["first"]),) + FAN
    e = [c.ewm(span=n, adjust=False).mean() for n in lens]
    ups = [((a > b) & (a.shift(1) <= b.shift(1))).to_numpy() for a, b in zip(e[:-1], e[1:])]
    dns = [((a < b) & (a.shift(1) >= b.shift(1))).to_numpy() for a, b in zip(e[:-1], e[1:])]
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    who = -1
    for i in range(m):
        if who >= 0:
            if dns[who][i]:
                lx[i], who = True, -1
            continue
        for k in range(len(ups)):
            if ups[k][i]:
                le[i], who = True, k
                break
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
