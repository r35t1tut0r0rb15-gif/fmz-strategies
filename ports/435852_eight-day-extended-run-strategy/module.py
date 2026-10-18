"""Eight-bar run exhaustion fades, 1-hour bars: after more than eight bars with the close at or over its SMA 5, the first close under it goes
long (closed 11 bars after the signal); after more than eight bars at or under, the first close over it goes short (closed 11 bars
after).
Port of FMZ strategy #435852 "Eight Day Extended Run Strategy" (8DayRun).

FMZ source id: 435852

Source
    https://www.fmz.com/strategy/435852 (PineScript v4, FMZ last modified 2023-12-19 12:01:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 178-203), SMA 5; run of more than 8 bars; exit more than 10 bars after the signal
    TriggerBuy = barssince(close < SMA) > 8;  Buy = TriggerBuy[1] and close < SMA;  entry long (Buy);  close long when barssince(Buy) > 10;  Sell = TriggerSell[1] and close > SMA (TriggerSell = barssince(close > SMA) > 8);  entry short;  close short when barssince(Sell) > 10

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince(x) counts bars since x was last true (0 on the bar it is true). The time exit is an
      explicit exit signal 11 bars after the entry's signal (not max_hold_time); a later signal resets
      the count. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average run counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435852_run_exhaustion_fade"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [5, 10],
    "run": [8, 5],
}
DEFAULT_PARAMS = {"sma_len": 5, "run": 8, "hold": 10}


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


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i in range(len(cond)):
        if cond[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    under = (c < sma).to_numpy()
    over = (c > sma).to_numpy()
    run = int(p["run"])
    trig_buy = _barssince(under) > run
    trig_sell = _barssince(over) > run
    trig_buy1 = np.concatenate(([False], trig_buy[:-1]))
    trig_sell1 = np.concatenate(([False], trig_sell[:-1]))
    buy = trig_buy1 & under
    sell = trig_sell1 & over
    hold = int(p["hold"])
    lx = _barssince(buy) > hold
    sx = _barssince(sell) > hold
    ix = bars_df.index
    return (pd.Series(buy, index=ix), pd.Series(lx, index=ix), pd.Series(sell, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
