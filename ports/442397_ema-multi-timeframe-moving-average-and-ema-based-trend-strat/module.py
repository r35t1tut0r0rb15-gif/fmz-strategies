"""Pullback buys under a falling SMA 8, 1-hour bars, long only: from flat, a close under the SMA 10 that dips through the SMA 3 with the open above the EMA 5 while the SMA 8 falls goes long; the long closes
after 10 bars or after 5 closes above the fill.
Port of FMZ strategy #442397 "基于均线和EMA的跨时间框架趋势策略Multi-Timeframe-Moving-Average-and-EMA-Based-Trend-Strategy" (Free Strategy #02 (ES / SPY)).

FMZ source id: 442397

Source
    https://www.fmz.com/strategy/442397 (PineScript v3, FMZ last modified 2024-02-21 15:59:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-161), SMA 3 / 8 / 10, EMA 5; max profit closes 5; max bars 10; qty 1
    flat and close < sma10 and close <= sma3 and close[1] > sma3[1] and open > ema5 and sma8 < sma8[1] -> entry L1
    BarsSinceEntry = flat ? 0 : BarsSinceEntry[1] + 1;  MaxProfitCount += close > avg and BarsSinceEntry > 1;  BarsSinceEntry - 1 >= 10 or MaxProfitCount >= 5 -> close L1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters are ported as written (bars counted from the fill bar; profitable closes are close
      against the fill price). Long only. The qty of 1 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA pullback entry with bar / profit counters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442397_sma_pullback_bar_and_profit_count_exit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_profit_closes": [5, 3],
    "max_bars": [10, 20],
}
DEFAULT_PARAMS = {"max_profit_closes": 5, "max_bars": 10, "sma1": 3, "sma2": 8, "sma3": 10, "ema1": 5}


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
    o, c = bars_df["open"], bars_df["close"]
    s1 = c.rolling(int(p["sma1"])).mean()
    s2 = c.rolling(int(p["sma2"])).mean()
    s3 = c.rolling(int(p["sma3"])).mean()
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    go = ((c < s3) & (c <= s1) & (c.shift(1) > s1.shift(1)) & (o > e1) & (s2 < s2.shift(1))).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    mp, mb = int(p["max_profit_closes"]), int(p["max_bars"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, entry_i, bse, mpc = 0, -1, 0, 0
    for i in range(m):
        if held == 0:
            bse = mpc = 0
        else:
            bse += 1
            if cv[i] > ov[entry_i] and bse > 1:
                mpc += 1
        if held == 0 and go[i] and i + 1 < m:
            le[i], held, entry_i = True, 1, i + 1
        elif held == 1 and (bse - 1 >= mb or mpc >= mp):
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
