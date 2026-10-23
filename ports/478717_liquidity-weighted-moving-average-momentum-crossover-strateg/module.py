"""Broker days, long only: the close is recorded on each bar where volume per unit of candle body crosses over its EMA 10 plus one 10-bar deviation; the EMA 50 of that recorded close crossing over its EMA 100 goes long, crossing under closes it.
Port of FMZ strategy #478717 "Liquidity Weighted Moving Average Momentum Crossover Strategy" (Liquidity Weighted Moving Averages [AlgoAlpha]).

FMZ source id: 478717

Source
    https://www.fmz.com/strategy/478717 (PineScript v6, FMZ last modified 2025-01-17 15:45:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 114-163), liquidity = volume / abs(close - open); boundary EMA 10 + stdev 10; EMA 50 / 100 of the last recorded close
    priceMovementLiquidity = volume / abs(close - open);  crossover(liquidity, ema(liquidity, 10) + stdev(liquidity, 10)) -> array.insert(values, 0, close)
    fastEMA = ema(values[0], 50);  slowEMA = ema(values[0], 100);  crossover(fast, slow) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The array starts with five na values, so the averages start at the first liquidity crossover and
      then follow a step series (the latest recorded close). A doji (open = close) makes the liquidity a
      division by zero, which is na; an na in the 10-bar window makes the boundary na. The EMAs start at
      the first recorded close. Long only. Commission and slippage are costs. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings of liquidity-sampled closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) per unit of candle body; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478717_liquidity_sampled_close_ema50_100_cross_long_only"
FAMILY = "liquidity_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [100, 50],
}
DEFAULT_PARAMS = {"outlier": 10, "fast": 50, "slow": 100}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    liq = v / (c - o).abs().where(c != o)            # division by zero is na
    n = int(p["outlier"])
    bound = liq.ewm(span=n, adjust=False).mean() + liq.rolling(n).std(ddof=0)
    hit = ((liq > bound) & (liq.shift(1) <= bound.shift(1))).to_numpy()
    cn = c.to_numpy(dtype=float)
    rec = np.full(len(cn), np.nan)
    last = np.nan
    for i in range(len(cn)):
        if hit[i]:
            last = cn[i]
        rec[i] = last
    rec = pd.Series(rec, index=c.index)
    f = rec.ewm(span=int(p["fast"]), adjust=False).mean()
    s = rec.ewm(span=int(p["slow"]), adjust=False).mean()
    buy = (f > s) & (f.shift(1) <= s.shift(1))
    sell = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
