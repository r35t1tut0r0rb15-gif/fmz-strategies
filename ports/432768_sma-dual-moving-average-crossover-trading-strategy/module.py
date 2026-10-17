"""SMA 14 / 28 crosses, 4-hour bars: the SMA 14 crossing above the SMA 28 goes long, crossing below goes short; longs carry
a bracket that, as written, sits about 10 % from the fill (prices passed as tick counts); shorts carry none.
Port of FMZ strategy #432768 "双SMA均线交叉交易策略Dual-Moving-Average-Crossover-Trading-Strategy" (Strategy Template (ST v1.0)).

FMZ source id: 432768

Source
    https://www.fmz.com/strategy/432768 (PineScript v5, FMZ last modified 2023-11-21 12:26:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 204-288), SMA 14 / 28, TP 1 %, SL 1 % (passed as prices to the tick arguments)
    crossover(sma14, sma28) -> (close_all if short) entry long;  crossunder -> (close_all if long) entry short
    long: exit(from "Buy to Open", profit = avg x 1.01, loss = avg x 0.99)  -- PRICES passed as TICK distances
    short: exit(from "Buy to Open", ...)  -- bound to the long entry, so shorts get no exit order

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN (as #427674): `profit` and `loss` take tick counts, so the long bracket distances are
      the price levels times the tick size: on the source's BTC_USDT (tick 0.1) about 10.1 % above and
      9.9 % below the fill. Ported as percentages of the fill (tp_pct 10.1 / sl_pct 9.9); the grid
      adds the evident 1 % / 1 %. Decision owed: the intended version.
    * The short side's exit names the long entry ("Buy to Open"), so shorts have no stop or target:
      ported as written. The positions flip on the crosses (close_all before the entry): REVERSAL
      INTENDED. The position size and compounding are sizing. Stops on 4-hour bars: mark
      coarse_bar_stop. Stop module: portfolio_kwargs {} (driver D4). FREQ = "4h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick-scaled distances -> percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital-based position size, compounding and commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432768_sma_cross_long_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [10.1, 1.0],
    "sl_pct": [9.9, 1.0],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "tp_pct": 10.1, "sl_pct": 9.9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _ = _signals(bars_df, p)
    sl = pd.Series(np.where(le, float(p["sl_pct"]) / 100, np.nan), index=bars_df.index)
    tp = pd.Series(np.where(le, float(p["tp_pct"]) / 100, np.nan), index=bars_df.index)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
