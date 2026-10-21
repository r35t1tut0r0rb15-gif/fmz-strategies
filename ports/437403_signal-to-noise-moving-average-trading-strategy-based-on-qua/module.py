"""Signal-to-noise line against its SMA, 30-minute bars: with the previous bar's S/N value (-10 ln of the average reciprocal close over 20 earlier bars) above its 7-bar SMA the state is long, below it short, equal
flat (close all); reversing.
Port of FMZ strategy #437403 "Signal to Noise Moving Average Trading Strategy Based on Quantitative Trading" (StoN).

FMZ source id: 437403

Source
    https://www.fmz.com/strategy/437403 (PineScript v4, FMZ last modified 2024-01-02 12:24:35).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 154-175), length 21, smooth 7, reverse off
    StN = -10 log(sum over i = 1 .. 20 of (1 / close[i]) / 21);  SMAStN = sma(StN, 7)
    pos = -1 if SMAStN[1] > StN[1], 1 if SMAStN[1] < StN[1], else 0;  entry Long / Short on possig, close_all on 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * log is the natural logarithm; the sum runs over i = 1 .. length - 1 and is divided by length, as
      written. Comparing the line with its own average is scale-free. The state is a level, so the entry is
      sent on every bar of the state; state 0 closes. REVERSAL INTENDED. No sizing code. FREQ = "30min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a log-price line against its own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437403_signal_to_noise_sma_state"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 42],
    "smooth": [7, 14],
}
DEFAULT_PARAMS = {"length": 21, "smooth": 7, "reverse": False}


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
    n = int(p["length"])
    s = sum((1.0 / c.shift(i)) / n for i in range(1, n))
    with np.errstate(divide="ignore", invalid="ignore"):
        stn = -10 * np.log(s)
    sm = stn.rolling(int(p["smooth"])).mean()
    a, b = sm.shift(1).to_numpy(), stn.shift(1).to_numpy()
    with np.errstate(invalid="ignore"):
        pos = np.where(a > b, -1.0, np.where(a < b, 1.0, 0.0))
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
