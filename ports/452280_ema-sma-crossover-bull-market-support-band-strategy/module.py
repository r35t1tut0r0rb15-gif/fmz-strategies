"""EMA 21 / SMA 20 crossings confirmed by the bar's direction, daily bars: the EMA 21 crossing over the SMA 20 on an up close goes long, crossing under on a down close goes short; an unconfirmed cross only closes the opposite trade; reversing.
Port of FMZ strategy #452280 "EMA SMA Crossover Bull Market Support Band Strategy" (EMA-SMA Crossover Strategy).

FMZ source id: 452280

Source
    https://www.fmz.com/strategy/452280 (PineScript v5, FMZ last modified 2024-05-23 18:11:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 78-123), EMA 21 / SMA 20; capital 1000
    crossover(ema21, sma20) and close > close[1] -> entry Buy;  crossunder and close < close[1] -> entry Sell
    crossunder(ema21, sma20) -> close Buy;  crossover -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes: on a confirmed cross the entry reverses the opposite
      trade and the close then finds it reversed; on an unconfirmed cross only the close acts, leaving
      the position flat. The two crossings cannot meet on one bar. REVERSAL INTENDED. The capital
      setting is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, confirmed MA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital setting stored.
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

NAME = "fmz_452280_ema21_sma20_confirmed_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [20, 50],
    "ema_len": [21, 50],
}
DEFAULT_PARAMS = {"sma_len": 20, "ema_len": 21}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    fast = c.rolling(int(p["sma_len"])).mean()
    slow = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    buy = (slow > fast) & (slow.shift(1) <= fast.shift(1))
    sell = (slow < fast) & (slow.shift(1) >= fast.shift(1))
    up, dn = c > c.shift(1), c < c.shift(1)
    le, se = buy & up, sell & dn
    return le, sell & ~se, se, buy & ~le


def portfolio_kwargs(**params):
    return {}
