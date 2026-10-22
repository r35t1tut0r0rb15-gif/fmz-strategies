"""Zero-lag MACD (zero-lag EMA 12 minus zero-lag EMA 26) crossing its zero-lag signal (9), 1-hour bars: crossing up goes long, crossing down goes short; reversing.
Port of FMZ strategy #448772 "ZeroLag-MACD-多空策略-ZeroLag-MACD-Long-Short-Strategy" (ZL_MACD Strategy (Zero Lag MACD Strategy)).

FMZ source id: 448772

Source
    https://www.fmz.com/strategy/448772 (PineScript v4, FMZ last modified 2024-04-18 17:06:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-159), fast 12, slow 26, signal 9; EMA mode; 'real' zero-lag signal (Glaz algo off); MACD EMA 9 (unused)
    zl(n) = 2 ema(close, n) - ema(ema(close, n), n);  macd = zl(12) - zl(26);  signal = 2 ema(macd, 9) - ema(ema(macd, 9), 9);  crossover -> entry Buy;  crossunder -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default is the "real" zero-lag signal (useOldAlgo off). No exit: positions end at the
      opposite entry. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zero-lag MACD signal crossings.
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

NAME = "fmz_448772_zero_lag_macd_signal_cross_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def _zl(x, n):
    e = _ema(x, n)
    return 2 * e - _ema(e, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = _zl(c, p["fast"]) - _zl(c, p["slow"])
    sig = _zl(macd, p["signal"])
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
