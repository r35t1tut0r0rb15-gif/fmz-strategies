"""Close against an SMA 64 in an SMA 200 trend, broker days: the close dipping below the SMA 64 with both above the SMA 200
goes long, rising above it with both below goes short; the opposite cross closes; as written only the short carries the
1 % / 3 % bracket (fixed at the fill).
Port of FMZ strategy #430569 "Golden Cross Death Cross Moving Average Trading Strategy" (XAU M15).

FMZ source id: 430569

Source
    https://www.fmz.com/strategy/430569 (PineScript v5, FMZ last modified 2023-10-30 14:42:09).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 152-201), SMA 64 vs SMA 1 (the close), trend SMA 200, stop 1 %, target 3 %
    enterLong = crossover(sma64, close) and sma64 > sma200 and close > sma200 -> entry long
    enterShort = crossunder(sma64, close) and sma64 < sma200 and close < sma200 -> entry short
    crossunder(sma64, close) -> close long;  crossover(sma64, close) -> close short
    every bar: exit("Take Profit/Stop Loss", "Long", stop = close x 0.99, limit = close x 1.03)
               exit("Take Profit/Stop Loss", "Short", stop = close x 1.01, limit = close x 0.97)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Short MA Length" 1 makes the short MA the close. Both exits share one id and are re-issued
      every bar, the short's last: the order is re-bound to the short entry on every bar, so a long
      has no bracket (it leaves by the cross) and a short has it (as #430368). The levels come from
      each bar's close (moving): rule 2, mark trailing_stop_pending; the port fixes them at the fill
      (sl_stop 0.01, tp_stop 0.03 for shorts).
    * A cross that enters one side also closes the other (a reversal): REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the shared-id exit read as written, the moving levels fixed at the fill.
    2 generic: PASS, moving averages and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exit percentages quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430569_sma64_close_cross_trend"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_length": [64, 32],
    "trend_length": [200, 100],
}
DEFAULT_PARAMS = {"long_length": 64, "trend_length": 200, "short_sl": 0.01, "short_tp": 0.03}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    lm = c.rolling(int(p["long_length"])).mean()
    tm = c.rolling(int(p["trend_length"])).mean()
    xo = (lm > c) & (lm.shift(1) <= c.shift(1))      # crossover(long_ma, close)
    xu = (lm < c) & (lm.shift(1) >= c.shift(1))      # crossunder(long_ma, close)
    long_e = (xo & (lm > tm) & (c > tm)).astype(bool)
    short_e = (xu & (lm < tm) & (c < tm)).astype(bool)
    return long_e, xu.astype(bool), short_e, xo.astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, long_x, short_e, short_x = _signals(bars_df, p)
    return long_e, long_x & ~short_e, short_e, short_x & ~long_e


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, short_e, _ = _signals(bars_df, p)
    idx = bars_df.index
    sl = pd.Series(np.where(short_e, p["short_sl"], np.nan), index=idx)
    tp = pd.Series(np.where(short_e, p["short_tp"], np.nan), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
