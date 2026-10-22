"""Fair-value-gap continuation, daily bars: a bullish gap (the low of the previous bar over the high three bars back) with the close at or over the 3-bar midpoint goes long with a target 0.12 % over the signal bar's high; a bearish gap with the close at or under the midpoint goes short with a target 0.6 % under its low; reversing. The moving stop is not ported (pending).
Port of FMZ strategy #452736 "FVG动量短线交易策略-FVG-Momentum-Scalping-Strategy" (ScalpingStrategy (FVG momentum)).

FMZ source id: 452736

Source
    https://www.fmz.com/strategy/452736 (PineScript v5, FMZ last modified 2024-05-28 17:23:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-152), 3-bar range; long target high x 1.0012, short target low x 0.994; stop max(low3 x 0.997, avg x 0.995) / min(high3 x 1.003, avg x 1.005) re-sent every bar
    low[1] > high[3] and close >= mid3 and low <= high3 -> entry Buy, exit(Target, limit = high x 1.0012);  high[1] < low[3] and close <= mid3 and high >= low3 -> entry Sell, exit(Target, limit = low x 0.994)
    every bar: exit(Stop Loss, Buy, stop = max(lowest(low, 3) x 0.997, avg x 0.995));  exit(Stop Loss, Sell, stop = min(highest(high, 3) x 1.003, avg x 1.005))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is fixed on the signal bar from its high (low): ported as a fraction of the signal
      close (high x 1.0012 / close - 1 for a long, 1 - low x 0.994 / close for a short), read at the
      fill bar from the signal bar. The stop is re-sent every bar from the moving 3-bar extreme and
      the average price (na while flat), so it starts after the fill and moves: stops() cannot express
      it, it is not ported and the module gets the mark trailing_stop_pending (as #437800, #438034).
      A repeat signal inside the trade re-issues the target from that bar (also pending). The 'low <=
      high3' test always holds. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target as a fraction of the signal close; the moving stop pending (mark).
    2 generic: PASS, fair-value-gap continuation entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452736_fvg_continuation_signal_extreme_target_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_tp": [1.0012, 1.01],
    "short_tp": [0.994, 0.99],
}
DEFAULT_PARAMS = {"long_tp": 1.0012, "short_tp": 0.994}


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


def _signals(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    l3, h3 = lo.rolling(3).min(), h.rolling(3).max()
    mid = (l3 + h3) / 2
    buy = (lo.shift(1) > h.shift(3)) & (c >= mid) & (lo <= h3)
    sell = (h.shift(1) < lo.shift(3)) & (c <= mid) & (h >= l3)
    return buy, sell


def simulate(bars_df, **params):
    buy, sell = _signals(bars_df)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    buy, sell = _signals(bars_df)
    tp = pd.Series(np.nan, index=bars_df.index)
    tp = tp.mask(buy, h * float(p["long_tp"]) / c - 1).mask(sell, 1 - lo * float(p["short_tp"]) / c)
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
