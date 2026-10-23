"""The SMA 5 of the close crossing the session VWAP of hlc3, 2-hour bars: crossing over goes long, crossing under goes short; reversing.
Port of FMZ strategy #427307 "Simple Moving Average Crossover with Stop Loss Strategy" (ROoT).

FMZ source id: 427307

Source
    https://www.fmz.com/strategy/427307 (PineScript v5, FMZ last modified 2023-09-19 21:42:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-170), SMA 5; vwap(hlc3); the EMA 9 "stoploss" is unused; margin 1 / 1
    crossover(sma(close, 5), vwap(hlc3)) -> entry BUY;  crossunder(sma(close, 5), vwap(hlc3)) -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * vwap(hlc3) is anchored at the broker-day start (17:00 America/New_York), as #363564. The EMA 9 named
      stoploss is never used by an order. REVERSAL INTENDED. The margin settings are sizing. FREQ = "2h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA against the session VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin_long / margin_short 1 stored, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwap(hlc3), anchored at the broker-day start; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427307_sma5_session_vwap_cross_reversal"
FAMILY = "vwap_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [5, 10],
}
DEFAULT_PARAMS = {"sma_len": 5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    day = broker_day(c.index)
    pv = (v * (h + lo + c) / 3).groupby(day).cumsum()
    cvol = v.groupby(day).cumsum()
    vwap = pd.Series((pv / cvol.where(cvol != 0)).to_numpy(), index=c.index)
    s = c.rolling(int(p["sma_len"])).mean()
    le = (s > vwap) & (s.shift(1) <= vwap.shift(1))
    se = (s < vwap) & (s.shift(1) >= vwap.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
