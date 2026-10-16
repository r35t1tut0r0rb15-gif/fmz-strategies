"""One red candle then three green, 1-hour bars, long only from flat: a red bar whose low is under the next three bars'
lows, followed by three green bars with rising closes, goes long with a stop at the red bar's low and a 1 R target.
Port of FMZ strategy #430364 "1-3-1-红绿K线反转策略1-3-1-Red-Green-Candlestick-Reversal-Strategy" (Strategie tradosaure 1 Bougie Rouge suivi de 3 Bougies Vertes).

FMZ source id: 430364

Source
    https://www.fmz.com/strategy/430364 (PineScript v5, FMZ last modified 2023-10-27 16:00:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 161-207), stop = low[3], target = close + (close - stop)
    redCandle = close[3] < open[3] and low[3] < low[2], low[1], low
    greenCandles = three green bars; higherClose = close > close[1] > close[2]
    redCandle and greenCandles and higherClose and flat -> entry long; stop = low[3]; tp = close + (close - stop)
    long: exit(stop = stop, limit = tp)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the signal bar (stop = the red bar's low, target 1 R above the signal
      close), as fractions of the signal close shifted one bar (re-based on the fill).
    * Entries only from flat (position_size == 0): "flat" follows the house bracket on bars.
      Opposite entries cannot occur. Long only. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, bar colours, lows and a 1 R target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430364_red_then_three_green_bracket_long"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"rr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    red = (c.shift(3) < o.shift(3)) & (lo.shift(3) < lo.shift(2)) & (lo.shift(3) < lo.shift(1)) & (lo.shift(3) < lo)
    green = (c > o) & (c.shift(1) > o.shift(1)) & (c.shift(2) > o.shift(2))
    higher = (c > c.shift(1)) & (c.shift(1) > c.shift(2))
    sig = (red & green & higher).to_numpy()
    sl_frac = ((c - lo.shift(3)) / c).to_numpy()
    return sig, sl_frac, sl_frac * float(p["rr"])


def _run(bars_df, p):
    buy, sl_f, tp_f = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_):
                pos = 0
        if pos == 0 and buy[i] and sl_f[i] > 0:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl_f[i], tp_f[i]
            sl_arr[i], tp_arr[i] = s_, t_
    return le, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
