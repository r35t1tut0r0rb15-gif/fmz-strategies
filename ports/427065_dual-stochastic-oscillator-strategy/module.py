"""Double stochastic: with the slow stochastic (97) above 50, a fast stochastic (5, EMA 2) turning
up below 30 goes long; with the slow one below 50, the fast one turning down above 70 goes short.
A long is closed once the close reaches 1.2 x the close of the previous long signal, a short once
the close reaches the previous short signal's close / 1.2.
Port of FMZ strategy #427065 "Dual Stochastic Oscillator Strategy".

FMZ source id: 427065

Source
    https://www.fmz.com/strategy/427065 (PineScript v4, FMZ last modified 2023-09-17 18:26:16).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 148-200), K 5 smooth 2, K 97 smooth 1, factor 1.2
    k = ema(stoch(close, high, low, 5), 2); k1 = ema(stoch(close, high, low, 97), 1)
    buy  = k1 > 50 and k < 30 and k > k[1] -> entry long
    sell = k1 < 50 and k > 70 and k < k[1] -> entry short
    close >= valuewhen(buy, close, 1) x 1.2 -> close long
    close <= valuewhen(sell, close, 1) / 1.2 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(syminfo.tickerid, timeframe.period, x) is the chart's own series x.
    * stoch includes the current bar (Pine); ema(x, 1) is x itself (the "D 3" input is unused).
    * valuewhen(cond, close, 1) is the close of the SECOND most recent signal bar (occurrence 1;
      occurrence 0 is the latest, the current bar included), as Pine defines it. So the exit level
      refers to the previous signal, not to the entry; it is ported as written.
    * strategy.entry reverses: REVERSAL INTENDED. On a bar with an opposite entry and a close of the
      side held, the reversal wins (Pine fills the entry after the close). From flat, closes do
      nothing.
    * The two 1.2 factors are price ratios (dimensionless), kept.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a price ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (one unit per signal).
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

NAME = "fmz_427065_double_stochastic"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_k": [5, 9],
    "slow_k": [97, 60],
    "exit_factor": [1.2, 1.05],
}
DEFAULT_PARAMS = {"fast_k": 5, "fast_smooth": 2, "slow_k": 97, "slow_smooth": 1, "exit_factor": 1.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _stoch(bars, n):
    """Pine stoch: 100 x (close - lowest(low, n)) / (highest(high, n) - lowest(low, n)), current bar included."""
    lo = bars["low"].rolling(n).min()
    hi = bars["high"].rolling(n).max()
    return 100 * (bars["close"] - lo) / (hi - lo)


def _valuewhen(cond, src, occurrence):
    """Pine valuewhen(cond, src, occurrence): src at the (occurrence+1)-th most recent bar where cond is true."""
    c = cond.to_numpy(dtype=bool)
    v = src.to_numpy(dtype=float)
    hits = v[c]
    count = np.cumsum(c)              # signals up to and including each bar
    k = count - 1 - occurrence        # index into hits
    out = np.full(len(v), np.nan)
    ok = k >= 0
    out[ok] = hits[k[ok]]
    return pd.Series(out, index=src.index)


def _positions(long_c, long_x, short_c, short_x):
    """Pine order semantics on completed bars: from flat an entry opens; an opposite entry reverses;
    a close exits the side held; the opposite entry wins over a close; long is tested first."""
    m = len(long_c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and long_x[i]:
            pos = 0
        elif pos == -1 and short_x[i]:
            pos = 0
        tgt[i] = pos
    return tgt


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
    c = bars_df["close"]
    k = _stoch(bars_df, int(p["fast_k"])).ewm(span=int(p["fast_smooth"]), adjust=False).mean()
    k1 = _stoch(bars_df, int(p["slow_k"])).ewm(span=int(p["slow_smooth"]), adjust=False).mean()
    buy = (k1 > 50) & (k < 30) & (k > k.shift(1))
    sell = (k1 < 50) & (k > 70) & (k < k.shift(1))
    close_long = c >= _valuewhen(buy, c, 1) * p["exit_factor"]
    close_short = c <= _valuewhen(sell, c, 1) / p["exit_factor"]
    tgt = _positions(buy.to_numpy(), close_long.to_numpy(), sell.to_numpy(), close_short.to_numpy())
    le, lx, se, sx = _emit(tgt, bars_df.index)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
