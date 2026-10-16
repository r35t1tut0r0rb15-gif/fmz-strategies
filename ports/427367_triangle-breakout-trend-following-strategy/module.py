"""TrianglePoint, long only: an inside bar against the previous 9 closes (low above their lowest,
high below their highest) while EMA 13 is above EMA 200 goes long; EMA 13 crossing under EMA 65, or a
close 5 % under the entry price, closes the long.
Port of FMZ strategy #427367 "Triangle Breakout Trend Following Strategy".

FMZ source id: 427367

Source
    https://www.fmz.com/strategy/427367 (PineScript v4, FMZ last modified 2023-09-20 14:24:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 154-206), bars 9, EMA 13 / 65 / 200, stop 5 %
    tri = low > lowest(close[1], 9) and high < highest(close[1], 9)
    ema13 > ema200 and tri and flat -> entry long (adds while below the average price: pyramiding 2)
    crossunder(ema13, ema65) -> close; close < avg x (1 - 5 %) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The add below the average price (pyramiding 2, fixed qty 3) is sizing (criterion 4, stored);
      the port holds one position, so the average price is the entry fill (the next open).
    * The 5 % stop is a close test (rule 3): an exit signal. takeProfitVal is computed but never
      used by an order.
    * Long only; one signal per bar.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-based exits.
    2 generic: PASS, bar counts and a stop as a fraction of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding / fixed qty stored in original_sizing.txt.
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

NAME = "fmz_427367_triangle_point_long"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "num_periods": [9, 5],
    "slow_ema": [65, 30],
    "stop_pct": [5.0, 2.5],
}
DEFAULT_PARAMS = {"num_periods": 9, "fast_ema": 13, "slow_ema": 65, "trend_ema": 200, "stop_pct": 5.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["num_periods"])
    hh, ll = c.shift(1).rolling(n).max(), c.shift(1).rolling(n).min()
    tri = (lo > ll) & (h < hh)
    f = c.ewm(span=int(p["fast_ema"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_ema"]), adjust=False).mean()
    t = c.ewm(span=int(p["trend_ema"]), adjust=False).mean()
    entry = ((f > t) & tri).to_numpy()
    xcross = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    stop = p["stop_pct"] / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, avg = 0, False, np.nan
    for i in range(m):
        if pending:
            pos, pending, avg = 1, False, ov[i]
        if pos == 1:
            if xcross[i] or cv[i] < avg * (1 - stop):
                lx[i], pos = True, 0
        elif not pending and entry[i]:
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
