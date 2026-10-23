"""Hourly bars, long only: the close crossing above the session VWAP while still under its SWMA arms a setup; the first bar the close also clears the SWMA goes long; a target of 250 ticks and a stop of 2500 ticks (about 0.06 % and 0.6 % of the source's BTC price; the two inputs are swapped in the exit call).
Port of FMZ strategy #437561 "Price Momentum Tracking Strategy" (Simple Price Momentum (SPM)).

FMZ source id: 437561

Source
    https://www.fmz.com/strategy/437561 (PineScript v4, FMZ last modified 2024-01-03 17:32:14).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 213-234), stop loss 250 (ticks), reward / risk 10 (take profit 2500 ticks); consecutive orders off
    triggerLong = vwapLong and not vwapLong[1] and not swmaLong and not swmaLong[1];  saveLong := trigger ? true : not vwapLong ? false : saveLong[1];  startLong = saveLong and swmaLong and not startLong[1]
    startLong -> entry Open Long;  exit(profit = stopLoss (250), loss = takeProfit (2500))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit passes the "stop loss" (250) as profit and the "take profit" (2500) as loss: a 250-tick
      target and a 2500-tick stop, as written (weird case). Criterion 2: on the header's BTC_USDT (0.1
      tick, about 42000 USD in the 2023-12 .. 2024-01 window) that is 25 / 250 USD, ported as fractions of
      the fill 0.000595 and 0.00595 (as #437390). vwap(close) is the session VWAP, anchored at the
      broker-day start (as earlier ports); swma is the 4-bar 1-2-2-1 average. startLong's [1] reads its own
      final value (the rising edge of the setup). Long only. 100 % of equity and the commission are sizing
      and costs. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed fractional bracket from the fill.
    2 generic: PASS, VWAP and SWMA momentum re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only; tick distances converted at the source's BTC price).
    4 signals only: strategy(): 100 % of equity, capital 20000, commission 0.025 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the session VWAP of the close; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437561_vwap_swma_momentum_setup_tick_bracket_long"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.000595, 0.002],
    "sl": [0.00595, 0.01],
}
DEFAULT_PARAMS = {"tp": 0.000595, "sl": 0.00595}


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
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    swma = (c.shift(3) + 2 * c.shift(2) + 2 * c.shift(1) + c) / 6
    sl_ = (c > swma).to_numpy()
    vl = (c > vwap).to_numpy()
    m = len(sl_)
    le = np.zeros(m, dtype=bool)
    save, prev_start = False, False
    for i in range(m):
        vl1 = vl[i - 1] if i else False
        sl1 = sl_[i - 1] if i else False
        trig = vl[i] and not vl1 and not sl_[i] and not sl1
        save = True if trig else (False if not vl[i] else save)
        start = save and sl_[i] and not prev_start
        le[i] = start
        prev_start = start
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
