"""Top / bottom divergence with stop and target (Zer3192): the MACD histogram crossing below zero on
a lower close goes short; crossing above zero on a higher close goes long; 1 % stop and 1 % target
on the entry price.
Port of FMZ strategy #402455 "顶/底背离指标观察系统 with 止盈止损".

Source
    https://www.fmz.com/strategy/402455 (PineScript v5, author Zer3192, FMZ last modified
    2023-03-02 22:39:32). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 38-75), MACD 12 / 26 / 9, stop 1 %, target 1 %
    macd = 2 (diff - ema(diff, 9));  top = crossunder(macd, 0) and close[1] > close
    bot = crossover(macd, 0) and close[1] < close
    top (not short) -> entry short; else bot (not long) -> entry long
    stop / target at avg price -+ 1 %

Interpretation choices (Pine rules in SURVEY_README.md)
    * The defaults are the input() defaults (1 % / 1 %); the header's args set the stop to 99 %.
    * Fixed fractions of the entry price: sl_stop = tp_stop = 0.01, shifted one bar in stops().
      Stops on daily bars: coarse_bar_stop.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_402455_macd_zero_cross_bracket"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_pct": [1.0, 5.0, 99.0],
    "tp_pct": [1.0, 3.0, 5.0],
}
DEFAULT_PARAMS = {"stop_pct": 1.0, "tp_pct": 1.0}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    c = bars_df["close"]
    diff = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    macd = 2 * (diff - diff.ewm(span=9, adjust=False).mean())
    top = ((macd < 0) & (macd.shift(1) >= 0) & (c.shift(1) > c)).to_numpy()
    bot = ((macd > 0) & (macd.shift(1) <= 0) & (c.shift(1) < c)).to_numpy()
    return _always_in(bot, top, bars_df.index, short_first=True)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return {"sl_stop": pd.Series(p["stop_pct"] / 100, index=idx).shift(1),
            "tp_stop": pd.Series(p["tp_pct"] / 100, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
