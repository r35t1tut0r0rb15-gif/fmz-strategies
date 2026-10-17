"""ALMA 20 / 40 crosses confirmed by a rising MACD histogram, 1-hour bars: a fast ALMA crossing above the slow one with the
MACD 6 / 25 / 9 histogram rising goes long; the mirror goes short. Longs carry a 20 % stop (their 200 % target is out of
reach); shorts carry a 5 % target (their 100 % stop is out of reach).
Port of FMZ strategy #434285 "Full Crypto Swing ALMA Cross MACD Quantitative Strategy" (Full Crypto Swing Strategy ALMA Cross).

FMZ source id: 434285

Source
    https://www.fmz.com/strategy/434285 (PineScript v4, FMZ last modified 2023-12-05 10:24:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 162-194), ALMA 20 / 40, offset 0.9, sigma 5; MACD 6 / 25 / 9; long TP 200 % / SL 20 %, short TP 5 % / SL 100 %; HA candles off
    long = crossover(alma20, alma40) and hist > hist[1];  short = crossunder and hist < hist[1]
    exit long (profit = close x 2.0 / mintick, loss = close x 0.2 / mintick);  exit short (profit = close x 0.05 / mintick, loss = close x 1.0 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar with distances sized from the latest close, so the levels move
      after entry: stops() cannot express that (mark trailing_stop_pending). The port fixes them as
      fractions of the fill: long sl 0.20 (tp 2.0 kept, unreachable in practice), short tp 0.05 (the
      100 % stop is dropped). The side is taken from the signal (read on the fill bar).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent exits fixed at entry (approximation stated).
    2 generic: PASS, ALMA crosses, a MACD slope and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_434285_alma_cross_macd_swing"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [20, 10],
    "slow": [40, 80],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 40, "offset": 0.9, "sigma": 5.0, "m_fast": 6, "m_slow": 25, "m_sig": 9,
                  "tp_long": 2.0, "sl_long": 0.2, "tp_short": 0.05}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _alma(v, n, offset, sigma):
    mm = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - mm) ** 2) / (2 * s * s))
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (w / w.sum())
    return out


def _signals(bars_df, p):
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    f = pd.Series(_alma(cv, int(p["fast"]), float(p["offset"]), float(p["sigma"])), index=c.index)
    s = pd.Series(_alma(cv, int(p["slow"]), float(p["offset"]), float(p["sigma"])), index=c.index)
    macd = c.ewm(span=int(p["m_fast"]), adjust=False).mean() - c.ewm(span=int(p["m_slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["m_sig"]), adjust=False).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1)) & (hist > hist.shift(1))).to_numpy()
    se = ((f < s) & (f.shift(1) >= s.shift(1)) & (hist < hist.shift(1))).to_numpy()
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    sl = pd.Series(np.where(le, float(p["sl_long"]), np.nan), index=ix)
    tp = pd.Series(np.where(le, float(p["tp_long"]), np.where(se, float(p["tp_short"]), np.nan)), index=ix)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
