"""Breakouts over an old 120-bar high above the EMA 50, daily bars, long only (spot): the close crossing over the 120-bar high as it stood 80 or 120 bars ago, with the close over the EMA 50, buys with a 2 % stop from the signal close; a close under the EMA 50 sells.
Port of FMZ strategy #452714 "Trend-Following-with-Breakout-and-Frequency-Filter-Long-Only-基于突破和频率过滤的趋势跟踪策略只做多" (Trend Following with Breakout and Frequency Filter (Long Only)).

FMZ source id: 452714

Source
    https://www.fmz.com/strategy/452714 (PineScript v5, FMZ last modified 2024-05-28 14:00:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-144), EMA 50; highest(high, 120) taken 80 / 120 bars back; stop 2 % of the signal close; min hold 10 x timeframe.multiplier (milliseconds)
    (crossover(close, hh120[80]) or crossover(close, hh120[120])) and close > ema50 and time - lastEntry > 10 -> entry, exit(stop = close x 0.98), lastEntry = time
    close < ema50 and long and time - lastEntry > 10 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'minimum hold' compares bar times in milliseconds with minHoldBars x timeframe.multiplier =
      10, so it only blocks a second signal or exit on the same bar: in effect no hold filter. The
      stop is fixed on the signal bar from its close: ported as the fixed fraction 0.02 of the fill
      (as #437751). A repeat signal inside the trade re-issues the stop from that bar's close, which
      stops() cannot express: the port keeps the opening level and marks trailing_stop_pending (as
      #434428). The signal and the exit cannot meet on one bar (close over against under the EMA).
      Spot account: Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop as a fixed fraction; re-issued stops pending (mark).
    2 generic: PASS, old-high breakouts in an EMA uptrend.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452714_lagged_120bar_high_breakout_ema50_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [50, 100],
    "lb_min": [80, 40],
    "sl_pct": [0.02, 0.05],
}
DEFAULT_PARAMS = {"ema_len": 50, "lb_min": 80, "lb_max": 120, "sl_pct": 0.02}


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
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    hh = bars_df["high"].rolling(int(p["lb_max"])).max()
    c1 = c.shift(1)
    le = False
    for k in (int(p["lb_min"]), int(p["lb_max"])):
        lvl = hh.shift(k)
        le = le | ((c > lvl) & (c1 <= lvl.shift(1)))
    le = le & (c > ema)
    lx = c < ema
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
