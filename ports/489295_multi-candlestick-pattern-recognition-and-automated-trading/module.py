"""Morning and evening stars with a 0.5 % / 1 % bracket, broker days: a strong bearish candle, a small middle candle
and a strong bullish candle closing above the first one's midpoint goes long; the mirror goes short; each trade has
a 0.5 % stop and a 1 % target.
Port of FMZ strategy #489295 "多重蜡烛形态识别与自动交易策略-Multi-Candlestick-Pattern-Recognition-and-Automated-Trading-Strategy" (Morning & Evening Star Strategy (1% TP, 0.5% SL)).

FMZ source id: 489295

Source
    https://www.fmz.com/strategy/489295 (PineScript v6, FMZ last modified 2025-04-03 11:10:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 183-239), SL 0.5 %, TP 1 %
    strong body > 60 % of range; small body < 30 % (or < 40 % with a wick > 30 %) for the middle candle
    morning = bearish strong [2], middle [1], bullish strong [0], close > midpoint of [2];  evening mirrored
    entry + exit(loss = 0.5 % x close, profit = 1 % x close)   (in the tick arguments)

Interpretation choices (Pine rules in SURVEY_README.md)
    * loss / profit take ticks; the author passes price distances (a percentage of the close): read as price
      distances (as #427592): sl_stop 0.5 %, tp_stop 1 % of the fill (scalars).
    * Entries reverse (REVERSAL INTENDED); the two patterns cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill.
    2 generic: PASS, candle proportions and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489295_morning_evening_star_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.5, 1.5],
    "tp_pct": [1.0, 3.0],
}
DEFAULT_PARAMS = {"sl_pct": 0.5, "tp_pct": 1.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body, rng = (c - o).abs(), h - lo
    strong = body > rng * 0.6
    small = body < rng * 0.3
    upw, low_w = h - np.maximum(o, c), np.minimum(o, c) - lo
    middle = small | ((body < rng * 0.4) & ((upw > rng * 0.3) | (low_w > rng * 0.3)))
    mid3 = (o.shift(2) + c.shift(2)) / 2
    morning = ((c.shift(2) < o.shift(2)) & strong.shift(2, fill_value=False) & middle.shift(1, fill_value=False)
               & (c > o) & strong & (c > mid3))
    evening = ((c.shift(2) > o.shift(2)) & strong.shift(2, fill_value=False) & middle.shift(1, fill_value=False)
               & (c < o) & strong & (c < mid3))
    false = pd.Series(False, index=bars_df.index)
    return morning.astype(bool), false, evening.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
