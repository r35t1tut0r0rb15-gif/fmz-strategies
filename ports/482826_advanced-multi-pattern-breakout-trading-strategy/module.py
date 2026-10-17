"""Candle-pattern breakouts, always in, daily bars: a green candle after a green breakout of the prior high, or a
doji / hammer / pin bar crossing the prior high, goes long; the red mirrors go short.
Port of FMZ strategy #482826 "高级多重形态突破交易策略-Advanced-Multi-Pattern-Breakout-Trading-Strategy" (Target(Made by Karan)).

FMZ source id: 482826

Source
    https://www.fmz.com/strategy/482826 (PineScript v5, FMZ last modified 2025-02-20 13:33:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 95-212)
    breakout_green = crossover(close, high[1]) and close[1] > open[1]; second_green = close > open and
    breakout_green[1] -> entry "Buy"; red mirrored with crossunder(close, low[1]) -> entry "Sell"
    doji (body <= 10 % of range), hammer (body <= 30 % of range, open - low > 2 body, high - close <= 0.3 body),
    pin bar (one shadow > 2 body, the other < body), each with crossover(close, high[1]) -> long entries,
    with crossunder(close, low[1]) -> short entries

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pattern tests are ported as written (the hammer's shadows use open and close, not the body's ends).
    * The lookback input and the start / end prices only feed drawings: no effect on the orders.
    * All long entries share the position (pyramiding 1), as do the shorts; entries reverse (REVERSAL INTENDED), so
      the strategy is always in after the first signal. A bar with both a long and a short pattern (rare: a green
      candle closing below the prior low) emits neither (ambiguous order of the two reversals).
    * Signal module, no stops. Daily bars are broker days (17:00 America/New_York), stamped with their first minute;
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle proportions and prior-bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (1 trial), before any backtest; the source has no signal
      parameter.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482826_candle_pattern_breakouts_always_in"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    doji = body <= rng * 0.1
    hammer = (body <= rng * 0.3) & (o - lo > 2 * body) & (h - c <= body * 0.3)
    upper_sh, lower_sh = h - np.maximum(o, c), np.minimum(o, c) - lo
    pin = ((upper_sh > body * 2) & (lower_sh < body)) | ((lower_sh > body * 2) & (upper_sh < body))
    ph, pl = h.shift(1), lo.shift(1)
    x_up = (c > ph) & (c.shift(1) <= ph.shift(1))
    x_dn = (c < pl) & (c.shift(1) >= pl.shift(1))
    green, red = c > o, c < o
    brk_green = x_up & green.shift(1, fill_value=False)
    brk_red = x_dn & red.shift(1, fill_value=False)
    pattern = doji | hammer | pin
    long_c = (green & brk_green.shift(1, fill_value=False)) | (pattern & x_up)
    short_c = (red & brk_red.shift(1, fill_value=False)) | (pattern & x_dn)
    long_e = (long_c & ~short_c).astype(bool)
    short_e = (short_c & ~long_c).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
