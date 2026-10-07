"""Smarter MACD: at each MACD-histogram cross above zero the signal-line value is latched as the
"bottom"; a higher bottom than the previous one goes long. At each cross below zero the signal is
latched as the "top"; a lower top goes short (always in).
Port of FMZ strategy #363579 "Smarter MACD".

Source
    https://www.fmz.com/strategy/363579 (PineScript v4, FMZ last modified 2022-05-16 17:05:05).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 91-163), MACD 12 / 26, signal EMA 23
    macdBot := crossover(hist, 0) ? signal : macdBot[1]   (0 on the first bar)
    macdTop := crossunder(hist, 0) ? signal : macdTop[1]
    macdBot > macdBot[1] -> entry long; else macdTop < macdTop[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The average-bottom / average-top lines and the monitor table only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363579_macd_rising_bottoms"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [26, 34],
    "signal": [9, 23],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 23}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    hist = macd - sig
    x_up = ((hist > 0) & (hist.shift(1) <= 0)).to_numpy()
    x_dn = ((hist < 0) & (hist.shift(1) >= 0)).to_numpy()
    sv = sig.to_numpy()
    m = len(c)
    bot, top = np.zeros(m), np.zeros(m)
    for i in range(1, m):
        bot[i] = sv[i] if x_up[i] else bot[i - 1]
        top[i] = sv[i] if x_dn[i] else top[i - 1]
    prev_bot = np.concatenate([[np.nan], bot[:-1]])
    prev_top = np.concatenate([[np.nan], top[:-1]])
    return _always_in(bot > prev_bot, top < prev_top, bars_df.index)


def portfolio_kwargs(**params):
    return {}
