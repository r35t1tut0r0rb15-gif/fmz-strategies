"""Zero-lag MACD sign (always in): the DEMA 12 - DEMA 26 line above zero goes long, below zero goes
short.
Port of FMZ strategy #426360 "Zero Lag MACD DEMA Breakout Strategy".

Source
    https://www.fmz.com/strategy/426360 (PineScript v4, FMZ last modified 2023-09-11 14:43:52).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 81-108), DEMA 12 / 26
    DEMA(n) = 2 * ema(close, n) - ema(ema(close, n), n)
    line = DEMA(12) - DEMA(26);  line > 0 -> entry long;  line < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signal-line DEMA (9) only plots. The test-period window (2000-2100) is always true.
    * strategy() is commented out in the source; FMZ's defaults apply (sizing out of scope).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426360_zero_lag_macd_sign"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [26, 40],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
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


def _dema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    return 2 * e1 - e1.ewm(span=n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    line = _dema(c, int(p["fast"])) - _dema(c, int(p["slow"]))
    return _always_in((line > 0).to_numpy(), (line < 0).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
