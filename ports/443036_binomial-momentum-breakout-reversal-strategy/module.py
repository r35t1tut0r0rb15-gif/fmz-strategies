"""HPotter combo of the 123 reversal and Gimelfarb's Bull Power value, 1-hour bars: long when the 123 state is long and the bull-power value is small, short when the 123 state is short and the value is
large, flat otherwise; reversing.
Port of FMZ strategy #443036 "Binomial Momentum Breakout Reversal Strategy" (Combo Backtest 123 Reversal & Bull Power).

FMZ source id: 443036

Source
    https://www.fmz.com/strategy/443036 (PineScript v4, FMZ last modified 2024-02-28 17:20:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-222), 123: stochastic 14, K smoothing 1, D 3, level 50; Bull Power sell level 15, buy level 3 (price units); reverse off
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  mirrored -> -1;  else previous
    value = bull-power case table on open / high / low / close / close[1];  value > 15 -> -1;  value <= 3 -> 1;  else previous;  both agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 15 / 3 levels compare a price difference: as fractions of the close at the BTC
      reading of 42000, 3.57e-4 and 7.1e-5 of the close. The case table is ported as written (several
      branches compare close[1] with the current open). Both states are levels; disagreement closes.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430543 (3 members, best partner #430543, Jaccard 0.749); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443036_reversal123_bull_power_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "sell_frac": [3.57e-04, 0.002],
}
DEFAULT_PARAMS = {"length": 14, "sell_frac": 3.57e-04, "buy_frac": 7.1e-05, "k_smoothing": 1, "d_length": 3,
                  "level": 50.0, "reverse": False}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    s = 0
    for i in range(len(up)):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        out[i] = s
    return out


def _bull_value(o, h, lo, c, c1):
    a = np.where(c1 < o, np.maximum(h - c1, c - lo), np.maximum(h - o, c - lo))
    b = np.where(c1 > o, h - lo, np.maximum(o - c1, h - lo))
    d1 = np.where(c1 < o, np.maximum(h - c1, c - lo), h - o)
    d2 = np.where(c1 > o, h - lo, np.maximum(o - c, h - lo))
    d3 = np.where(c1 > o, np.maximum(h - o, c - lo), np.where(c1 < o, np.maximum(o - c, h - lo), h - lo))
    eq = np.where(h - c > c - lo, d1, np.where(h - c < c - lo, d2, d3))
    return np.where(c < o, a, np.where(c > o, b, eq))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    a = _state(((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy(),
               ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy())
    cv = c.to_numpy(dtype=float)
    val = _bull_value(o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float), cv,
                      c1.to_numpy(dtype=float))
    with np.errstate(invalid="ignore"):
        sell = val > float(p["sell_frac"]) * cv
        buy = val <= float(p["buy_frac"]) * cv
    m = len(cv)
    b = np.zeros(m, dtype=np.int8)
    s = 0
    for i in range(m):
        if sell[i]:
            s = -1
        elif buy[i]:
            s = 1
        b[i] = s
    tgt = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
