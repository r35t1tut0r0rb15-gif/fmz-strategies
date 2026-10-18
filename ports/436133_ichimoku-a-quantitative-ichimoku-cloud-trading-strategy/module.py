"""Ichimoku position-and-cross combinations, 1-hour bars: a cross of the close, the Kijun or the Tenkan over the displaced cloud top, when the other two lines already sit above it, goes long;
the mirror under the displaced cloud floor goes short (reversing).
Port of FMZ strategy #436133 "Ichimoku云图量化交易策略A-Quantitative-Ichimoku-Cloud-Trading-Strategy" (Ichimoku Cloud).

FMZ source id: 436133

Source
    https://www.fmz.com/strategy/436133 (PineScript v3, FMZ last modified 2023-12-21 15:33:05).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 142-211), conversion 9, base 26, span B 52, displacement 26
    maxlead / minlead = max / min of the two spans; A = kijun > maxlead[26], E = tenkan > maxlead[26], I = close > maxlead[52]; B / F / J = their crossovers
    A and E and J -> entry long;  A and I and F -> entry long;  E and I and B -> entry long;  C, G, K (under minlead) with L, H, D (their crossunders) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The displaced spans are read 26 and 52 bars back (past values only). One cross event with the
      other two lines already beyond the cloud makes each entry. strategy.entry reverses: REVERSAL
      INTENDED. The cash order size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cloud crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash order size and capital stored.
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

NAME = "fmz_436133_ichimoku_cloud_cross_combos"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 7],
    "displacement": [26, 20],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "span_b": 52, "displacement": 26}


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


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def donchian(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    conv, base = donchian(int(p["conversion"])), donchian(int(p["base"]))
    lead1 = (conv + base) / 2
    lead2 = donchian(int(p["span_b"]))
    maxlead, minlead = np.maximum(lead1, lead2), np.minimum(lead1, lead2)
    d = int(p["displacement"])
    mx1, mn1, mx2, mn2 = maxlead.shift(d), minlead.shift(d), maxlead.shift(2 * d), minlead.shift(2 * d)
    A, B = base > mx1, _xo(base, mx1)
    C, D = base < mn1, _xu(base, mn1)
    E, F = conv > mx1, _xo(conv, mx1)
    G, H = conv < mn1, _xu(conv, mn1)
    I, J = c > mx2, _xo(c, mx2)
    K, L = c < mn2, _xu(c, mn2)
    buy = ((A & E & J) | (A & I & F) | (E & I & B)).fillna(False)
    sell = ((C & G & L) | (C & K & H) | (G & K & D)).fillna(False)
    false = pd.Series(False, index=bars_df.index)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
