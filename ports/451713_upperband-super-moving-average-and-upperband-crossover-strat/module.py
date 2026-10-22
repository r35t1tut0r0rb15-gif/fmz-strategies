"""Breakouts over the SMA 20 of a range-scaled 'upperband', daily bars, long only: the close crossing over it while over its EMA 3 buys; a close under the EMA 3 sells.
Port of FMZ strategy #451713 "超级均线与Upperband交叉策略-Super-Moving-Average-and-Upperband-Crossover-Strategy" (Estratégia de Cruzamento de Bandas (Super MA and Upperband crossover)).

FMZ source id: 451713

Source
    https://www.fmz.com/strategy/451713 (PineScript v5, FMZ last modified 2024-05-17 13:50:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-144), factor 0.001; length 20; upperband = high x (1 + 2 x (range / mid x 1000) x factor); EMA 3
    close[1] <= sma(upper, 20)[1] and close > sma(upper, 20) and close > ema3 -> bought, entry Compra;  else close < ema3 and bought -> not bought, close Compra

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'bought' flag is set with each entry and cleared with each close, so it follows the
      position; the close comes only on a bar without a buy signal. Long only. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, breakouts over a range-scaled band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451713_range_scaled_upperband_breakout_ema3_exit_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [0.001, 0.0005],
    "length": [20, 50],
}
DEFAULT_PARAMS = {"factor": 0.001, "length": 20, "ema_len": 3}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    upper = h * (1 + 2 * (((h - lo) / ((h + lo) / 2)) * 1000) * float(p["factor"]))
    band = upper.rolling(int(p["length"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    buy = (c.shift(1) <= band.shift(1)) & (c > band) & (c > ema)
    sell = (c < ema) & ~buy
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
