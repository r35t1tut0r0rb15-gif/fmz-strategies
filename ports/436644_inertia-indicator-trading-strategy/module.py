"""Inertia (smoothed relative volatility index) side, 1-hour bars: the 10-bar deviation of the close smoothed on up bars against down bars as a 0-100 index, EMA 14; over 50 is long, under 50 short (reversing); the earlier state
holds at 50; an optional switch trades the reverse.
Port of FMZ strategy #436644 "Inertia Indicator Trading Strategy" (Inertia Indicator).

FMZ source id: 436644

Source
    https://www.fmz.com/strategy/436644 (PineScript v2, FMZ last modified 2023-12-26 15:42:33).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 146-167), period 10, smooth 14, reverse off
    StdDev = stdev(close, 10);  u = StdDev on up closes, d = StdDev on the other bars;  nU = (13 nU[1] + u) / 14, nD likewise;  nRVI = 100 nU / (nU + nD);  nRes = ema(nRVI, 14)
    pos = 1 if nRes > 50, -1 if nRes < 50, else pos[1];  possig = -pos when reverse;  entry Long / Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The deviation is the population form. The state is a level, so the entry is sent on every bar of the
      state; a same-side entry while in the position is ignored (pyramiding 0). REVERSAL INTENDED. The
      default quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility index state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427893 (2 members, best partner #427893, Jaccard 0.757); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436644_inertia_rvi_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 20],
    "smooth": [14, 7],
}
DEFAULT_PARAMS = {"period": 10, "smooth": 14, "reverse": False}


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
    sd = c.rolling(int(p["period"])).std(ddof=0).to_numpy()
    upc = (c > c.shift(1)).to_numpy()
    m = len(sd)
    n_u = np.full(m, np.nan)
    n_d = np.full(m, np.nan)
    pu = pd_ = 0.0
    for i in range(m):
        u = sd[i] if upc[i] else 0.0
        d = 0.0 if upc[i] else sd[i]
        n_u[i] = (13.0 * pu + u) / 14.0
        n_d[i] = (13.0 * pd_ + d) / 14.0
        pu = 0.0 if np.isnan(n_u[i]) else n_u[i]
        pd_ = 0.0 if np.isnan(n_d[i]) else n_d[i]
    with np.errstate(divide="ignore", invalid="ignore"):
        rvi = pd.Series(100.0 * n_u / (n_u + n_d), index=bars_df.index)
    res = rvi.ewm(span=int(p["smooth"]), adjust=False).mean().to_numpy()
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if res[i] > 50:
                prev = 1.0
            elif res[i] < 50:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
