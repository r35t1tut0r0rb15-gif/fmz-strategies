"""LazyBear squeeze momentum with a ROC "moving" filter (Kiasaki template), 1-hour bars: the momentum line above zero while
the EMA of the 30-bar ROC is beyond +-3 % holds a long, below zero holds a short; the source's 100 % stop is kept (a
short's stop at a doubled price), its 5000 % target cannot be reached.
Port of FMZ strategy #430881 "Dual Channel Tracking Reversal Strategy" (Squeeze X BF).

FMZ source id: 430881

Source
    https://www.fmz.com/strategy/430881 (PineScript v4, FMZ last modified 2023-11-02 16:31:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 218-318), KC 22, ROC 30 / 7 %, SL 100 %, TP 5000 %
    val = linreg(close - avg(avg(highest(high, 22), lowest(low, 22)), sma(close, 22)), 22, 0)
    long = val > 0 and |ema(roc(close, 30), 30 / 2)| > 7 / 2 -> entry long;  short = val < 0 and moving -> entry short
    exit: stop = avg price x (1 -+ 100 %), limit = avg price x (1 +- 5000 %), from the bar after the signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(x, 22, 0) is the least-squares line of the last 22 values at the current bar. The BB / KC
      squeeze states are plot-only. Pine v4 integer division: the ROC EMA length 30 / 2 = 15 and the
      threshold 7 / 2 = 3 (as #365892).
    * sl_stop 1.0 for both sides as written (a long's stop sits at price 0); the 5000 % target is
      unreachable on either side and not emitted. vbt applies the stop from the fill bar, the source
      one bar later (as #365892). The time window is always true.
    * Entries are re-issued on every qualifying bar; strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed percentage stop.
    2 generic: PASS, a regression momentum line and ROC.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_430881_squeeze_momentum_roc"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "roc_len": [30, 60],
    "pcnt": [7, 3],
}
DEFAULT_PARAMS = {"kc_len": 22, "roc_len": 30, "pcnt": 7, "sl_pct": 100.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(x, n):
    xs = np.arange(n, dtype=float)
    sx, sxx = xs.sum(), (xs * xs).sum()

    def f(y):
        sy, sxy = y.sum(), (xs * y).sum()
        slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        return (sy - slope * sx) / n + slope * (n - 1)
    return x.rolling(n).apply(f, raw=True)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["kc_len"])
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    val = _linreg(c - mid, n)
    r = int(p["roc_len"])
    roc = 100 * (c - c.shift(r)) / c.shift(r)
    emaroc = roc.ewm(span=r // 2, adjust=False).mean()
    thr = int(p["pcnt"]) // 2
    moving = (emaroc > thr) | (emaroc < -thr)
    return ((val > 0) & moving).astype(bool), ((val < 0) & moving).astype(bool)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
