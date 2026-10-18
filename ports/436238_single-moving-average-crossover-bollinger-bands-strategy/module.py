"""Single SMA with a deviation band, 1-minute bars: the close crossing over the SMA 90 plus 0.9 sd, with the SMA rising for five bars, goes long; crossing under the SMA minus 0.9 sd, with the SMA
falling for five bars, goes short (reversing). The stop / target / trail inputs are all off.
Port of FMZ strategy #436238 "Single Moving Average Crossover Bollinger Bands Strategy" (single sma cross).

FMZ source id: 436238

Source
    https://www.fmz.com/strategy/436238 (PineScript v2, FMZ last modified 2023-12-22 14:10:14).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 132-161), SMA 90, band 0.9 stdev; take profit, stop and trail 0 (off)
    longCondition = crossover(close, sma + 0.9 stdev) and rising(sma, 5);  shortCondition = crossunder(close, sma - 0.9 stdev) and falling(sma, 5);  entry long / short with the explicit closes of the other side;  exit(...) with all arguments missing, when crossmid

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit orders carry no profit, loss or trail (the inputs are 0, so na): they do nothing. The
      explicit closes coincide with the reversal. rising(sa, 5) means the SMA grew on each of the last five
      bars. REVERSAL INTENDED. The full-equity size is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, exit orders without arguments: none.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the off bracket inputs stored.
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

NAME = "fmz_436238_sma_deviation_band_cross"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "s": [90, 60],
    "p": [0.9, 1.5],
}
DEFAULT_PARAMS = {"s": 90, "p": 0.9}


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


def _monotone(x, n, up):
    ok = pd.Series(True, index=x.index)
    for k in range(n):
        d = x.shift(k) - x.shift(k + 1)
        ok = ok & ((d > 0) if up else (d < 0))
    return ok


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["s"])
    sa = c.rolling(n).mean()
    band = c.rolling(n).std(ddof=0) * float(p["p"])
    hi, lo = sa + band, sa - band
    le = ((c > hi) & (c.shift(1) <= hi.shift(1)) & _monotone(sa, 5, True)).fillna(False).astype(bool)
    se = ((c < lo) & (c.shift(1) >= lo.shift(1)) & _monotone(sa, 5, False)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
