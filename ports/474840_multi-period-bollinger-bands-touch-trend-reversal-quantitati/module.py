"""First touches of the Bollinger 20 / 3.4 bands, 5-hour bars: a low first reaching the lower band goes long, a high first reaching the upper band goes short; a long closes on a high at or over the basis, a short on a low at or under it; reversing.
Port of FMZ strategy #474840 "Multi Period Bollinger Bands Touch Trend Reversal Quantitative Trading Strategy" (5-Min Bollinger Bands Touch Strategy).

FMZ source id: 474840

Source
    https://www.fmz.com/strategy/474840 (PineScript v5, FMZ last modified 2024-12-12 14:37:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-142), BB 20, 3.4 sd; margin 100 %
    low <= lower and low[1] > lower[1] -> entry Long;  high >= upper and high[1] < upper[1] -> entry Short;  high >= basis -> close Long;  low <= basis -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are bar-close tests sent every bar; a close acts only on the side held into the bar and
      not reversed on it (#437773), so a loop follows the position. The 5-hour bars are UTC-aligned
      5-hour blocks from the minute data. REVERSAL INTENDED. Margin settings only, no sizing code. FREQ =
      "5h" from the backtest header (the title's "5-Min" is not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, first band touches with basis exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin settings only.
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

NAME = "fmz_474840_bb20_3p4_first_touch_basis_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5h"  # backtest header period: 5h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [3.4, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 3.4}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    lc = ((lo <= dn) & (lo.shift(1) > dn.shift(1))).to_numpy()
    sc = ((h >= up) & (h.shift(1) < up.shift(1))).to_numpy()
    xl = (h >= basis).to_numpy()
    xs = (lo <= basis).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if lc[i] and nxt != 1:
            le[i], nxt = True, 1
        if sc[i] and nxt != -1:
            se[i], nxt = True, -1
        if xl[i] and pos == 1 and nxt == 1:
            lx[i], nxt = True, 0
        if xs[i] and pos == -1 and nxt == -1:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
