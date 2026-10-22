"""SMA 20 crossings, 2-minute bars: crossing up over the SMA 200 goes long, crossing down under the slow SMA 200 goes short; reversing.
Port of FMZ strategy #488239 "Flexible Moving Average Crossover Quantitative Strategy" (MA crossover strategy).

FMZ source id: 488239

Source
    https://www.fmz.com/strategy/488239 (PineScript v6, FMZ last modified 2025-03-26 11:01:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-227), fast SMA 20; slow SMA 200; long test against a fixed SMA 200; direction LongShort; 100 % of equity
    crossover(fastMA, sma(close, 200)) -> entry Long;  crossunder(fastMA, slowMA) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long test uses a fixed SMA 200 whatever the slow setting; the short test uses the slow average
      (an SMA 200 by default). Both directions are on by default: an entry on the other side reverses
      (REVERSAL INTENDED). MPL 2.0 source (the notice is kept: Mozilla Public License 2.0,
      © ccrockatt21700). FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_488239_sma20_200_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fastMAPeriod": [20, 50],
    "slowMAPeriod": [200, 100],
}
DEFAULT_PARAMS = {"fastMAPeriod": 20, "slowMAPeriod": 200}


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
    f = c.rolling(int(p["fastMAPeriod"])).mean()
    s = c.rolling(int(p["slowMAPeriod"])).mean()
    s200 = c.rolling(200).mean()
    le = (f > s200) & (f.shift(1) <= s200.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
