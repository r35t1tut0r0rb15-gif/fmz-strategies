"""Stochastic RSI with a ROC "moving" filter (Kiasaki template), 2-hour bars: K above D while the EMA of the 14-bar ROC is
beyond +-1 % holds a long, K below D holds a short; a 2 % stop and a 9 % target from the entry price.
Port of FMZ strategy #430880 "Coordinate Sliding Stop Loss Strategy" (Sto2).

FMZ source id: 430880

Source
    https://www.fmz.com/strategy/430880 (PineScript v4, FMZ last modified 2023-11-02 16:28:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 178-262), RSI 5 (SMA form), stoch 7, K 1, D 7, ROC 14 / 2 %, SL 2 %, TP 9 %
    k = sma(stoch(rsi, rsi, rsi, 7), 1); d = sma(k, 7); emaroc = ema(roc(close, 14), 14 / 2)
    long = k > d and |emaroc| > 2 / 2 -> entry long;  short = k < d and |emaroc| > 1 -> entry short
    exit long: stop = avg price x 0.98, limit = avg price x 1.09 (mirror short), from the bar after the signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI is the SMA (Cutler) form as written. Pine v4 integer division: the ROC EMA length is
      14 / 2 = 7 and the threshold 2 / 2 = 1 (as #365892).
    * The stop and target are fixed fractions of the entry price: sl_stop 0.02 and tp_stop 0.09 for
      both sides; vbt applies them from the fill bar, while the source places them one bar later
      (since_longEntry > 0), as #365892. The time window is always true.
    * Entries are re-issued on every qualifying bar (a re-entry after a stop exit); strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars:
      mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed percentage bracket.
    2 generic: PASS, stochastic RSI, ROC and percentage stops.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430880 (3 members, best partner #432979, Jaccard 0.698); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430880_stoch_rsi_roc_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "roc_len": [14, 28],
    "sl_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"rsi_len": 5, "stoch_len": 7, "smooth_k": 1, "smooth_d": 7, "roc_len": 14, "pcnt": 2,
                  "sl_pct": 2.0, "tp_pct": 9.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    c = bars_df["close"]
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).rolling(n).mean()
    dn = (-ch.clip(upper=0)).rolling(n).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    s = int(p["stoch_len"])
    lo_, hi_ = rsi.rolling(s).min(), rsi.rolling(s).max()
    k = (100 * (rsi - lo_) / (hi_ - lo_).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    r = int(p["roc_len"])
    roc = 100 * (c - c.shift(r)) / c.shift(r)
    emaroc = roc.ewm(span=r // 2, adjust=False).mean()
    thr = int(p["pcnt"]) // 2
    moving = (emaroc > thr) | (emaroc < -thr)
    return ((k > d) & moving).astype(bool), ((k < d) & moving).astype(bool)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
