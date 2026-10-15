"""Pure stochastic, long only: %K (10, smooth 7) above %D (4) in the oversold zone (K <= 20) with a
close at or above the previous high goes long; the long is closed when the close crosses under the
EMA 5, when K turns below D above the middle (50), or when K reaches 80.
Port of FMZ strategy #427302 "Pure Stochastic Long Only Strategy".

FMZ source id: 427302

Source
    https://www.fmz.com/strategy/427302 (PineScript (no @version line, v1 syntax), FMZ last modified 2023-09-19 21:22:11).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 152-176), length 10, OB 80, OS 20, K 7, D 4, EMA 5
    k = sma(stoch(close, high, low, 10), 7); d = sma(k, 4)
    k > d and k <= 20 and close >= high[1] -> entry long
    crossunder(close, ema 5) or (k < d and k > 50) or k >= 80 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only; entries only from flat; an exit is never on the entry's signal bar.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and price comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427302_pure_stochastic_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 14],
    "over_sold": [20, 30],
    "over_bought": [80, 70],
}
DEFAULT_PARAMS = {"length": 10, "over_bought": 80, "over_sold": 20, "smooth_k": 7, "smooth_d": 4, "ema_fast": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    st = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    ema = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    mid = (p["over_bought"] + p["over_sold"]) / 2
    entry = ((k > d) & (k <= p["over_sold"]) & (c >= h.shift(1))).to_numpy()
    exit_ = (((c < ema) & (c.shift(1) >= ema.shift(1))) | ((k < d) & (k > mid))
             | (k >= p["over_bought"])).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
