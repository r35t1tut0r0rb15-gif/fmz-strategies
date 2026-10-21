"""Daily-candle direction with an EMA 50 / 200 filter inside a UTC hour window, 45-minute bars: between 11:00 and 16:59 UTC, an up day (two days back) with the close above that day's open and the EMA 50
above the EMA 200 goes long, the mirror short; reversing; each trade trails by a small fixed amount once it is a larger fixed amount in profit, both re-expressed as fractions of the close.
Port of FMZ strategy #438466 "Daily Moving Average Tracking Strategy for Gold Value" (My Strategy).

FMZ source id: 438466

Source
    https://www.fmz.com/strategy/438466 (PineScript v4, FMZ last modified 2024-01-12 11:54:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-193), start hour 11, end hour 16; trailing start 100, step 10 (price units, divided by the tick into ticks)
    daily_open = security(D, open[1]);  daily_close = security(D, close[1]);  hour in 11..16
    long = daily_close > daily_open and close > daily_open and ema 50 > ema 200 and in hours -> entry Long;  short mirror -> entry Short;  exit(trail_points = 100 / mintick, trail_offset = 10 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar; its expression
      open[1] / close[1] is then the day before that, so both values are those of the broker day two days
      back, built from the module's own bars. hour is read on the bar's UTC open time (as #435514).
    * Criterion 2: the trail starts after a gain of 100 price units and trails 10 behind the best price;
      as the house percent trail: activate_after 0.0023 and pct 0.00023 are the reading (100 / 10 on BTC
      near 44000), 0.01 / 0.002 a wider pair (anchor high_low; mark trailing_stop). strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: ADAPT, price-unit trail -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trail inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC hours 11-16 of the bar; daily values from broker days.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438466_daily_candle_ema_hours_trail"
FAMILY = "trend_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.00023, 0.002],
    "activate": [0.0023, 0.01],
}
DEFAULT_PARAMS = {"trail_pct": 0.00023, "activate": 0.0023, "start_hour": 11, "end_hour": 16, "fast": 50,
                  "slow": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    day = broker_day(bars_df.index)
    d = bars_df.groupby(day).agg({"open": "first", "close": "last"})
    d_open = pd.Series(d["open"].shift(2).reindex(day).to_numpy(), index=c.index)   # completed day, then [1]
    d_close = pd.Series(d["close"].shift(2).reindex(day).to_numpy(), index=c.index)
    hr = bars_df.index.tz_convert("UTC").hour
    in_hours = pd.Series((hr >= int(p["start_hour"])) & (hr <= int(p["end_hour"])), index=c.index)
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (d_close > d_open) & (c > d_open) & (ef > es) & in_hours
    se = (d_close < d_open) & (c < d_open) & (ef < es) & in_hours
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
