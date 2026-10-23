"""Broker days: the 1-bar momentum crossing above 0 on volume over 2 x its SMA 20 goes long, crossing below 0 on such volume goes short; only short trades carry a bracket (target 0.08 %, stop 0.05 % of the signal close, from tick distances); reversing.
Port of FMZ strategy #435894 "Momentum and Volume Trading Strategy" (Momentum and Volume Bot).

FMZ source id: 435894

Source
    https://www.fmz.com/strategy/435894 (PineScript v5, FMZ last modified 2023-12-19 15:37:16).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 95-120), profit target 0.8, stop loss 0.5 (as close x % / 100 in ticks); volume threshold 2 x SMA 20
    buy = crossover(close - close[1], 0) and volume > 2 sma(volume, 20) -> entry Buy;  sell = crossunder(...) and volume > 2 sma -> entry Sell
    exit('Take Profit/Stop Loss', from_entry = 'Buy', profit = close x 0.8 / 100, loss = close x 0.5 / 100);  exit('Take Profit/Stop Loss', from_entry = 'Sell', same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits share one id, so the second call (from_entry 'Sell') replaces the first every bar: only
      shorts get the bracket, longs end only by the reversal (as #376263 / #429773; weird case). The
      distances are close x 0.8 / 100 and close x 0.5 / 100 TICKS (no / mintick): on the header's BTC_USDT
      (0.1 tick) that is 0.08 % and 0.05 % of the close, ten times tighter than the inputs read (criterion
      2, converted at the source's tick, as #437390; weird case). They are re-sent each bar from the latest
      close; the port fixes them at the signal close as fractions of the fill (mark trailing_stop_pending).
      REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars:
      mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only bracket at the signal close.
    2 generic: PASS, momentum zero crossings on volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only; tick distances converted at the source's tick).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 2 x sma(volume, 20); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_435894_momentum_zero_cross_volume_spike_short_bracket_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "volume_threshold": [2.0, 1.5],
    "vol_len": [20, 50],
}
DEFAULT_PARAMS = {"volume_threshold": 2.0, "vol_len": 20, "tp": 0.0008, "sl": 0.0005}


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
    c, v = bars_df["close"], bars_df["volume"]
    mom = c - c.shift(1)
    vok = v > v.rolling(int(p["vol_len"])).mean() * float(p["volume_threshold"])
    buy = (mom > 0) & (mom.shift(1) <= 0) & vok
    sell = (mom < 0) & (mom.shift(1) >= 0) & vok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy & ~sell, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    short_fill = se.shift(1, fill_value=False)          # only the 'Sell' entry keeps the shared exit
    sl_f = (float(p["sl"]) * k).where(short_fill)
    tp_f = (float(p["tp"]) * k).where(short_fill)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
