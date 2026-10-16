"""SMA 21 / 49 cross with a trailing buy, long only, 5-minute bars: after the fast SMA crosses above the slow
one, a buy level 4 % above the lowest low since the cross is tracked, and a bar whose high exceeds it buys;
the slow-above-fast cross closes the long.
Port of FMZ strategy #428782 "Trailing Buy Strategy" (Trailing Buy).

FMZ source id: 428782

Source
    https://www.fmz.com/strategy/428782 (PineScript v5, FMZ last modified 2023-10-09 14:53:02).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 308-364), SMA 21 / 49, trailing buy deviation 4 %, source high
    openLong = crossover(fastMA, slowMA); closeLong = crossunder(fastMA, slowMA)
    longBuyPrice = openLong and flat ? low x 1.04 : tryOpen ? min(low x 1.04, longBuyPrice[1] (nz 999999)) : na
    tryOpen = barssince(closeLong) >= barssince(openLong) and flat
    high > longBuyPrice -> entry long; closeLong -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The buy test reads the completed bar's high against a level from bars up to and including it
      (low x 1.04): a bar-close condition, filled at the next open. It is a resting-order idea
      evaluated on closes, as written (strategy.entry is a market order here).
    * While long the buy level is na. The date filter is the author's window (isWithinPeriod is
      true): dropped. Enable Trailing defaults to true and is fixed.
    * Long only. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the buy level is a close-checked condition.
    2 generic: PASS, percentages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and capital stored.
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

NAME = "fmz_428782_sma_cross_trailing_buy"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "deviation": [0.04, 0.02],
    "fast": [21, 10],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 49, "deviation": 0.04}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _bars_since(ev):
    out = np.full(len(ev), 999999, dtype=np.int64)
    last = -1
    for i, e in enumerate(ev):
        if e:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    op = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    cl = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    bs_open, bs_close = _bars_since(op), _bars_since(cl)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    dev = float(p["deviation"])
    m = len(hv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    lbp_prev = np.nan
    for i in range(m):
        lbp = np.nan
        if held:
            if cl[i]:
                lx[i], held = True, False
        else:
            if op[i]:
                lbp = lv[i] * (1 + dev)
            elif bs_close[i] >= bs_open[i]:
                lbp = min(lv[i] * (1 + dev), lbp_prev if not np.isnan(lbp_prev) else 999999.0)
            if not np.isnan(lbp) and hv[i] > lbp:
                le[i], held = True, True
        lbp_prev = lbp
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
