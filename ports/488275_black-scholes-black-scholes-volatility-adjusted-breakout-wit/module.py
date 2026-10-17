"""Expected-move breakouts with an SMA 20 filter, broker days: a close above the previous close plus one bar's expected
move (the previous close x the 20-bar standard deviation of log returns) and above the SMA 20 goes long; the mirror
goes short; the opposite signal reverses; the author's expected-move trail is pending.
Port of FMZ strategy #488275 "Black-Scholes波动率自适应突破策略与动态阈值优化-Black-Scholes-Volatility-Adjusted-Breakout-with-Dynamic-Threshold-Optimization" (Black-Scholes Expected Breakout Enhanced Bias-Free).

FMZ source id: 488275

Source
    https://www.fmz.com/strategy/488275 (PineScript v5, FMZ last modified 2025-03-26 14:34:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 222-288), volatility lookback 20, MA 20, trail multiplier 1.0 (SL 1 % /
TP 2 % only without the trail)
    volatility = stdev(log(close / close[1]), 20) x sqrt(ppy);  expectedMove = close[1] x volatility x sqrt(1 / ppy)
    long = close > close[1] + expectedMove and close > sma20 -> entry long (qty 5, pyramiding 5); short mirrored
    in a position: exit(trail_points = trail_offset = expectedMove x 1.0), re-issued every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * sqrt(ppy) cancels: the expected move is close[1] x the 20-bar standard deviation of log returns, whatever the
      chartRes input says.
    * Adds (pyramiding 5, qty 5) are sizing: net position only (#490570). Entries reverse (REVERSAL INTENDED).
    * The trail (rule 2, mark trailing_stop_pending): a price distance passed to tick arguments (read as a price
      distance, #427592), activation and offset both the current expected move, re-issued every bar (moving); a
      volatility measure other than ATR: not expressible in the house trail, not emitted. The 1 % / 2 % bracket
      applies only with the trail switched off (not the default): not ported.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail pending (mark).
    2 generic: PASS, a volatility-scaled threshold and a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty 5 / pyramiding quoted; the trail quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488275_expected_move_breakout"
FAMILY = "volatility_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_lookback": [20, 40],
    "ma_length": [20, 50],
}
DEFAULT_PARAMS = {"vol_lookback": 20, "ma_length": 20, "use_ma_filter": True}


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
    c1 = c.shift(1)
    move = c1 * np.log(c / c1).rolling(int(p["vol_lookback"])).std(ddof=0)
    ma = c.rolling(int(p["ma_length"])).mean()
    long_e = c > c1 + move
    short_e = c < c1 - move
    if p["use_ma_filter"]:
        long_e, short_e = long_e & (c > ma), short_e & (c < ma)
    false = pd.Series(False, index=bars_df.index)
    return long_e.astype(bool), false, short_e.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
