"""Four EMA-pair crosses as one net long, adds not ported, hourly bars: each of EMA 1 / 5, 3 / 10, 5 / 20 and 10 / 40
crossing up opens its own sub-position, closed when that pair's fast EMA is below its slow one; the port is long
while any sub-position is open.
Port of FMZ strategy #489304 "多重指数移动平均线交叉策略-Multi-EMA-Crossover-Strategy" (Multi-EMA Crossover Strategy).

FMZ source id: 489304

Source
    https://www.fmz.com/strategy/489304 (PineScript v5, FMZ last modified 2025-04-03 11:46:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 117-155), pairs EMA 1 / 5, 3 / 10, 5 / 20, 10 / 40, pyramiding 4
    crossover(fast_i, slow_i) -> entry "Long i";  fast_i < slow_i -> close "Long i"   (i = 1..4)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four named entries under pyramiding 4 are adds of 25 % each (sizing, criterion 4): the port emits the net
      position, long from the first sub-entry until the last one is closed. Each sub-position opens on its pair's
      cross up and closes on a bar where that pair's fast EMA is below the slow one; a cross and its close cannot
      fall on one bar. EMA 1 is the close itself.
    * Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 25 % per entry and pyramiding 4 quoted in original_sizing.txt.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489304_four_ema_pair_crosses_net_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}

PAIRS = ((1, 5), (3, 10), (5, 20), (10, 40))


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
    c = bars_df["close"]
    m = len(c)
    open_any = np.zeros(m, dtype=bool)
    for f, s in PAIRS:
        ef = c.ewm(span=f, adjust=False).mean()
        es = c.ewm(span=s, adjust=False).mean()
        up = ((ef > es) & (ef.shift(1) <= es.shift(1))).to_numpy()
        below = (ef < es).to_numpy()
        held = False
        sub = np.zeros(m, dtype=bool)
        for i in range(m):
            if up[i]:
                held = True
            if below[i]:
                held = False
            sub[i] = held
        open_any |= sub
    prev = np.concatenate(([False], open_any[:-1]))
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(open_any & ~prev, index=idx), pd.Series(prev & ~open_any, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
