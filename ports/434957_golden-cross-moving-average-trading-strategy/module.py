"""SMA 50 / 100 golden crosses, 1-minute bars, long only: the SMA 50 crossing above the SMA 100 goes long; the SMA 50 crossing
back below, a close under the SMA 100, or the SMA 100 crossing below the SMA 200 closes it; each trade also carries a 25 %
stop and a 300 % target.
Port of FMZ strategy #434957 "Golden Cross Moving Average Trading Strategy" ([LIVE] Golden Cross).

FMZ source id: 434957

Source
    https://www.fmz.com/strategy/434957 (PineScript v4, FMZ last modified 2023-12-11 11:37:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 150-223), SMA 50 / 100 / 200; TP 300 %, SL 25 % of the average price; dates 2018-2031
    crossover(sma50, sma100) -> entry long;  crossunder(sma50, sma100) or close < sma100 or crossunder(sma100, sma200) -> close long
    exit(profit = ticks to avg (1 + 300 %), stop = avg (1 - 25 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket uses the fill price: sl_stop 0.25, tp_stop 3.0. An exit signal on the bar of an
      entry signal acts on no position (the entry is not filled yet); the port drops it there and the
      next bar's test applies. The date window (2018 to 2031) is the author's: dropped.
    * Long only; an entry while long is ignored. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, average crosses and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434957_golden_cross_sma100_exit"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [50, 20],
    "sl_pct": [0.25, 0.05],
}
DEFAULT_PARAMS = {"fast": 50, "mid": 100, "slow": 200, "sl_pct": 0.25, "tp_pct": 3.0}


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
    f, md, s = (c.rolling(int(p[k])).mean() for k in ("fast", "mid", "slow"))
    le = ((f > md) & (f.shift(1) <= md.shift(1))).astype(bool)
    ex = ((f < md) & (f.shift(1) >= md.shift(1))) | (c < md) | ((md < s) & (md.shift(1) >= s.shift(1)))
    lx = (ex & ~le).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
