"""EMA 5 / 10 crossings at 10-bar close extremes, 1-hour bars, from flat: a cross up whose close is above the previous 10 closes goes long, a cross down whose close is below them goes short; the opposite
EMA crossing closes.
Port of FMZ strategy #446522 "Exponential Moving Average Crossover Quantitative Trading Strategy" (ema giao nhau (EMA 5 / 10 crossing at a 10-bar extreme)).

FMZ source id: 446522

Source
    https://www.fmz.com/strategy/446522 (PineScript v5, FMZ last modified 2024-03-29 10:59:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-154), EMA 5 / 10; 10-bar close extreme; 100 % of equity
    crossover and close > close[1..10] and flat -> entry Buy;  crossunder and close < close[1..10] and flat -> entry Sell;  long and crossunder -> close Buy;  short and crossover -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loops break on the first past close at or beyond the crossing close; a past close that does
      not exist yet does not break them. Entries only from flat (position_size == 0), so a crossing
      that closes a position never reverses it. The 100 % of equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings at close extremes, opposite-crossing exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446522_ema5_10_cross_at_10bar_extreme_from_flat"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 9],
    "slow": [10, 21],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 10, "lookback": 10}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    k = int(p["lookback"])
    pmax = c.shift(1).rolling(k, min_periods=1).max().to_numpy()   # missing past closes do not break the loop
    pmin = c.shift(1).rolling(k, min_periods=1).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        hi = xo & ((cv > pmax) | np.isnan(pmax))
        lw = xu & ((cv < pmin) | np.isnan(pmin))
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0:
            if hi[i]:
                le[i], pos = True, 1
            elif lw[i]:
                se[i], pos = True, -1
        elif pos == 1 and xu[i]:
            lx[i], pos = True, 0
        elif pos == -1 and xo[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
