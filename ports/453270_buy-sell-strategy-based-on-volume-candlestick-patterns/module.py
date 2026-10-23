"""Broker days: the SMA 60 crossing under an "accuracy" line (the EMA 10 on bars where the close crosses over the SMA 30, else the EMA 30) goes long; crossing over it goes short; reversing.
Port of FMZ strategy #453270 "Buy Sell Strategy Based on Volume Candlestick Patterns" (Buy/Sell with Volume and Candlestick Signals).

FMZ source id: 453270

Source
    https://www.fmz.com/strategy/453270 (PineScript v5, FMZ last modified 2024-06-03 16:31:28).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 99-181), SMA 10 / 30 / 60; EMA 10 / 30 / 3 / 7; SMA 9; volume SMA 20 (plots only)
    accuracy = crossover(close, sma30) ? ema10 : ema30;  buySignal = crossunder(sma60, accuracy) -> entry Enter Long;  sellSignal = crossover(sma60, accuracy) -> entry Enter Short
    close("Buy") when crossunder(sma9, ema7);  close("Sell") when crossover(sma9, ema7)  (ids never entered)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes name "Buy" / "Sell", but the entries are "Enter Long" / "Enter Short", so they never
      act (weird case): every signal reverses. The accuracy line jumps between two EMAs, which is what
      makes most crossings. The Fibonacci array, trend / volume lines and markers only plot: volume is not
      used. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA 60 crossings of a switching EMA line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453270_sma60_vs_switching_ema_accuracy_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_sma": [60, 100],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "long_sma": 60}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    fl, sl = int(p["fast"]), int(p["slow"])
    s_slow = c.rolling(sl).mean()
    x_up = (c > s_slow) & (c.shift(1) <= s_slow.shift(1))
    acc = c.ewm(span=fl, adjust=False).mean().where(x_up, c.ewm(span=sl, adjust=False).mean())
    s60 = c.rolling(int(p["long_sma"])).mean()
    buy = ((s60 < acc) & (s60.shift(1) >= acc.shift(1))).to_numpy()
    sell = ((s60 > acc) & (s60.shift(1) <= acc.shift(1))).to_numpy()
    m = len(buy)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        elif sell[i] and not buy[i] and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
