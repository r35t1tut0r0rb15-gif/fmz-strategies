"""Long whenever the close is above the EMA 200 and short whenever below, after the first SMA 9 / 15 cross of each
side; an opposite SMA 9 / 15 cross closes the trade for a bar, hourly bars.
Port of FMZ strategy #482515 "神经均线交叉趋势跟踪策略结合EMA过滤系统-Neural-Moving-Average-Crossover-Trend-Following-Strategy-with-EMA-Filtering-System" (SMA Crossover with EMA Filter).

FMZ source id: 482515

Source
    https://www.fmz.com/strategy/482515 (PineScript v5, FMZ last modified 2025-02-18 18:29:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 139-175), SMA 9 / 15, EMA 200
    crossover(sma9, sma15) and close > ema200 -> entry long; crossunder and close < ema200 -> entry short
    crossunder -> close long; crossover -> close short
    barssince(crossover) > 0 and close > ema200 -> entry long (re-entry); barssince(crossunder) > 0 and close <
    ema200 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The re-entries hold the side of the EMA 200 on every bar after the first cross of that side, so the strategy is
      nearly always in. A cross that closes the held side is followed in the script by a same-side re-entry on that
      bar; the re-entry meets the still-open position (pyramiding 1) and is ignored, so the trade is flat for one bar
      and re-entered on the next (as written; the order book is read at the bar's close).
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850); an exit and
      an opposite entry on one bar are emitted as the entry alone (reversal).
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMAs and an EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482515_ema200_side_sma9_15_cross_reentry"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [15, 30],
    "trend": [200, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 15, "trend": 200}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    ema = c.ewm(span=int(p["trend"]), adjust=False).mean()
    bull = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    bear = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    above, below = (c > ema).to_numpy(), (c < ema).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    seen_bull = seen_bear = False
    for i in range(m):
        start, tgt = pos, pos
        if bull[i] and above[i] and tgt != 1:
            le[i], tgt = True, 1
        if bear[i] and below[i] and tgt != -1:
            se[i], tgt = True, -1
        if bear[i] and start == 1 and tgt == 1:
            lx[i], tgt = True, 0
        if bull[i] and start == -1 and tgt == -1:
            sx[i], tgt = True, 0
        re_long = seen_bull and not bull[i] and above[i]           # barssince(crossover) > 0
        re_short = seen_bear and not bear[i] and below[i]
        if re_long and tgt != 1 and start != 1:
            le[i], tgt = True, 1
        if re_short and tgt != -1 and start != -1:
            se[i], tgt = True, -1
        if le[i] and sx[i]:
            sx[i] = False
        if se[i] and lx[i]:
            lx[i] = False
        seen_bull = seen_bull or bull[i]
        seen_bear = seen_bear or bear[i]
        pos = tgt
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
