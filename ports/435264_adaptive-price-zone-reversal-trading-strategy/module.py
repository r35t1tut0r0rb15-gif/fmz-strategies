"""Adaptive price zone fades, 1-minute bars: a low under the lower band goes long, a high over the upper band goes short
(reversing); between the bands the last side is kept; the "Trade reverse" input flips the side.
Port of FMZ strategy #435264 "Adaptive Price Zone Reversal Trading Strategy" (Adaptive Price Zone Backtest).

FMZ source id: 435264

Source
    https://www.fmz.com/strategy/435264 (PineScript v4, FMZ last modified 2023-12-13 16:33:33).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 187-206), APZ: double-smoothed EMA of the close and of the range, 5 bars (ceil of the square root of 20), bands 2 ranges wide; reverse input
    nP = ceil(sqrt(nPeriods));  xVal1 = ema(ema(close, nP), nP);  xVal2 = ema(ema(high - low, nP), nP);  UpBand = xVal1 + nBandPct xVal2;  DnBand = xVal1 - nBandPct xVal2
    pos = low < DnBand ? 1 : high > UpBand ? -1 : pos[1];  possig = reverse ? -pos : pos;  possig == 1 -> entry long;  possig == -1 -> entry short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state holds until the opposite band is touched; strategy.entry reverses: REVERSAL INTENDED.
      The zero state exists only before the first touch (nothing to close). A bar whose low is under
      the lower band and whose high is over the upper band takes the long side first, as the nested
      iff reads. A signal is sent on the change of state only. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435264_adaptive_price_zone_fade"
FAMILY = "volatility_band"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "n_periods": [20, 40],
    "band_pct": [2, 1],
}
DEFAULT_PARAMS = {"reverse": False, "n_periods": 20, "band_pct": 2}


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
    n = int(np.ceil(np.sqrt(int(p["n_periods"]))))
    v1 = c.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()
    v2 = (h - lo).ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()
    up = v1 + float(p["band_pct"]) * v2
    dn = v1 - float(p["band_pct"]) * v2
    to_long = (lo < dn).to_numpy()
    to_short = (h > up).to_numpy()
    m = len(to_long)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if to_long[i]:
            q = 1
        elif to_short[i]:
            q = -1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
