"""3-hour bars: the close crossing over the previous bar's 20-bar high on above-average volume goes long, crossing under the previous 20-bar low on such volume goes short; the opposite signal reverses (the channel exits can never fire).
Port of FMZ strategy #481339 "Dynamic Volume Enhanced Donchian Channel Trend Breakout Strategy" (Donchian Channels + Volume Strategy).

FMZ source id: 481339

Source
    https://www.fmz.com/strategy/481339 (PineScript v5, FMZ last modified 2025-02-10 14:18:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-165), Donchian 20 (previous bar for entries, current bar for exits); volume SMA 20; 10 % of equity
    longCondition = crossover(close, highest(high, 20)[1]) and volume > avgVolume -> entry Long;  shortCondition = crossunder(close, lowest(low, 20)[1]) and volume > avgVolume -> entry Short
    crossunder(close, lowest(low, 20)) -> close Long;  crossover(close, highest(high, 20)) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits compare the close with the CURRENT bar's channel, which includes the bar itself: a close
      can never be under its own bar's 20-bar low or over its 20-bar high, so neither exit can fire
      (weird case). Trades end only by the opposite entry, which reverses. REVERSAL INTENDED. 10 % of
      equity is sizing. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian breakouts on above-average volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481339_donchian20_breakout_volume_3h_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 55],
    "vol_len": [20, 50],
}
DEFAULT_PARAMS = {"period": 20, "vol_len": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["period"])
    up, dn = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    buy = (c > up) & (c.shift(1) <= up.shift(1)) & vol_ok
    sell = (c < dn) & (c.shift(1) >= dn.shift(1)) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
