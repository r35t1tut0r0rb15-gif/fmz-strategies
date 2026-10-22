"""Three-step EMA cross-ups after a TEMA-confirmed MACD cross, 2-hour bars, long only: once a MACD 13 / 18 cross over its SMA 14 signal with a rising TEMA 14 has armed the set-up, a bar where the EMA 9 crosses over the EMA 15 and the close crosses over the EMA 5 buys. The 7 / 100-point bracket re-sent every bar from the latest close is not ported (pending), so the long is held.
Port of FMZ strategy #473145 "Triple Moving Average Trend Following and Momentum Integration Quantitative Trading Strategy" (ITG Scalper Strategy).

FMZ source id: 473145

Source
    https://www.fmz.com/strategy/473145 (PineScript v5, FMZ last modified 2024-11-27 16:08:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-186), TEMA 14; MACD 13 / 18 with an SMA 14 signal; EMA 9 / 15 / 5; stop 7, target 100, trail 15 (points from the current close)
    crossover(macd, signal) and tema > tema[1] -> armed;  armed and crossover(ema9, ema15) and crossover(close, ema5) -> entry Long, disarm
    while long: sl = close - 7, tp = close + 100 (trail test close - sl > 15 never true) -> exit(stop, limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The set-up flag is armed by the filter cross and cleared by an entry, as written. The exit is
      re-sent on every bar from that bar's close (a stop 7 and a target 100 price units away; the trail
      test can never hold), so its levels move after entry: stops() cannot express a level re-set every
      bar, so it is kept pending (as #438034, mark trailing_stop_pending); with no other exit the port
      holds the first long until it is ported. Long only. No sizing code. FREQ = "2h" from the backtest
      header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, armed EMA cross-ups; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point bracket stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473145_tema_macd_armed_ema_cross_up_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [14, 21],
    "fast": [13, 12],
    "slow": [18, 26],
}
DEFAULT_PARAMS = {"len": 14, "fast": 13, "slow": 18, "signal": 14}


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


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["len"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    tema = 3 * (e1 - e2) + e3
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    arm = (_x(macd, sig) & (tema > tema.shift(1))).to_numpy()
    ema9, ema15, ema5 = (c.ewm(span=k, adjust=False).mean() for k in (9, 15, 5))
    go = (_x(ema9, ema15) & _x(c, ema5)).to_numpy()
    m = len(c)
    le = np.zeros(m, dtype=bool)
    armed = False
    for i in range(m):
        if arm[i]:
            armed = True
        if armed and go[i]:
            le[i], armed = True, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
