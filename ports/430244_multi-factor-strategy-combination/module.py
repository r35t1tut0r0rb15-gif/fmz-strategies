"""Stochastic + RSI double strategy (ChartArt's, in a combined script), 1-minute bars: the stochastic 14 crossing above its
signal while the stochastic RSI K is under 20, on a bar where RSI 14 crosses up through 30, goes long; the stochastic
crossing down above 80 with RSI crossing down through 70 goes short.
Port of FMZ strategy #430244 "Multi Factor Strategy Combination" (Stoch.RSI+RSI+DoubleStrategy+CMWilliamsVixFix+DMI).

FMZ source id: 430244

Source
    https://www.fmz.com/strategy/430244 (PineScript v3, FMZ last modified 2023-10-26 15:18:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 189-274), RSI 14, stochastic 14 / 3 / 3, levels 80 / 20 and 70 / 30
    k = sma(stoch(rsi, rsi, rsi, 14), 3); ks = sma(stoch(close, high, low, 14), 3); ds = sma(k, 3)
    crossover(ks, ds) and k < 20 and crossover(rsi, 30) -> entry long
    crossunder(ks, ds) and ks > 80 and crossunder(rsi, 70) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ds is the SMA 3 of the stochastic-RSI K (not of ks), and the long test reads k: kept as written.
    * The Williams Vix Fix and the DMI only plot. No exit other than the reversals.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels.
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

NAME = "fmz_430244_stoch_rsi_double"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_stoch": [14, 7],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"length_stoch": 14, "rsi_len": 14, "smooth_k": 3, "smooth_d": 3, "stoch_ob": 80, "stoch_os": 20,
                  "rsi_ob": 70, "rsi_os": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _stoch(src, h, lo, n):
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    return 100 * (src - ll) / (hh - ll).replace(0.0, np.nan)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, sk, sd = int(p["length_stoch"]), int(p["smooth_k"]), int(p["smooth_d"])
    r = _rsi(c, int(p["rsi_len"]))
    k = _stoch(r, r, r, n).rolling(sk).mean()
    ks = _stoch(c, h, lo, n).rolling(sk).mean()
    ds = k.rolling(sd).mean()
    xo = (ks > ds) & (ks.shift(1) <= ds.shift(1))
    xu = (ks < ds) & (ks.shift(1) >= ds.shift(1))
    r_xo = (r > p["rsi_os"]) & (r.shift(1) <= p["rsi_os"])
    r_xu = (r < p["rsi_ob"]) & (r.shift(1) >= p["rsi_ob"])
    le = (xo & (k < p["stoch_os"]) & r_xo).to_numpy()
    se = (xu & (ks > p["stoch_ob"]) & r_xu).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
