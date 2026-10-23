"""30-minute bars: the close minus the previous broker day's close, times the bar's volume, crossing over its average since the day began while the volume crosses over its 20-bar average goes long; both crossing under goes short; reversing.
Port of FMZ strategy #438500 "Quantitative Trading Strategy Quantity Trend Tracking Opening" (Lp-Op vol (avsr90)).

FMZ source id: 438500

Source
    https://www.fmz.com/strategy/438500 (PineScript v5, FMZ last modified 2024-01-12 14:46:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 93-134), daily resolution for the open price; volume SMA 20; intraday average length = bars since the day changed + 1
    Open_Price = security("D", close[1], lookahead_on);  Op_Cl_Vol = (close - Open_Price) * volume;  Avg = sma(Op_Cl_Vol, barssince(change(Open_Price)) + 1)
    crossover(Op_Cl_Vol, Avg) and crossover(volume, sma(volume, 20)) -> entry lo;  crossunder both -> entry sh

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("D", close[1], lookahead_on) is the previous day's close, known all day (the [1]
      pattern, no look-ahead); the port uses the previous broker day's last close. The average's length
      counts bars since the value last changed, so it is the mean of Op_Cl_Vol since the day began (the
      current bar included); before the first change it is one bar. round_to_mintick is left out (a
      rounding of the price difference). REVERSAL INTENDED. No sizing code. FREQ = "30min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, intraday change-weighted volume against its day average with a volume surge.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weight of the change since the previous day and in the volume crossing of its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: previous broker day's close (17:00 America/New_York); the day average restarts when it changes.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438500_day_change_volume_vs_day_average_volume_surge_30m_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_len": [20, 40],
}
DEFAULT_PARAMS = {"vol_len": 20}


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
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    prev_close = c.groupby(day).last().shift(1)          # the last COMPLETED broker day's close
    op = pd.Series(prev_close.reindex(day).to_numpy(), index=c.index)
    x = (c - op) * v
    chg = op.diff()
    seg = (chg.notna() & (chg != 0)).cumsum()
    started = seg > 0
    avg = x.groupby(seg).expanding().mean().reset_index(level=0, drop=True).reindex(c.index)
    avg = avg.where(started, x)                           # before the first change: a 1-bar average
    vb = v.rolling(int(p["vol_len"])).mean()
    co = (x > avg) & (x.shift(1) <= avg.shift(1)) & (v > vb) & (v.shift(1) <= vb.shift(1))
    cu = (x < avg) & (x.shift(1) >= avg.shift(1)) & (v < vb) & (v.shift(1) >= vb.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return co.astype(bool), false, cu.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
