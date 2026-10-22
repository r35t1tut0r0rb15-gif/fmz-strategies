"""Candle breakouts, broker days: a green candle after a green candle whose close crossed over the previous high, or a doji / hammer / pin bar closing over the previous high, goes long; the red mirrors (crossing under the previous low) go short; reversing, no other exit.
Port of FMZ strategy #482826 "Advanced Multi Pattern Breakout Trading Strategy" (Target(Made by Karan)).

FMZ source id: 482826

Source
    https://www.fmz.com/strategy/482826 (PineScript v5, FMZ last modified 2025-02-20 13:33:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-212), doji body <= 10 % of range; hammer / pin bar shapes; lookback 20 (target boxes only)
    green[1] and crossover(close, high[1]) one bar back, then close > open -> entry Buy;  red mirror with crossunder(close, low[1]) -> entry Sell
    isDoji / isHammer / isPinBar and crossover(close, high[1]) -> entries Buy Doji / Buy Hammer / Buy Pin Bar;  the same shapes and crossunder(close, low[1]) -> Sell Doji / Sell Hammer / Sell Pin Bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The shape tests are kept as written (the hammer's shadows read open - low and high - close, the pin
      bar either side). The recent high / low and the boxes are drawing only, so lookbackPeriod reaches
      no order. Default pyramiding refuses a second long under another id while long (as #441137); a
      short entry reverses a long and the other way round (REVERSAL INTENDED). When a long and a short
      call fire on one bar the short, called later, wins (as #437773). There is no other exit. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-shape breakouts of the previous bar.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482826_green_red_pair_doji_hammer_pin_prev_bar_break_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    body = (c - o).abs()
    rng = h - lo
    doji = body <= rng * 0.1
    hammer = (body <= rng * 0.3) & ((o - lo) > 2 * body) & ((h - c) <= body * 0.3)
    up_sh = h - np.maximum(o, c)
    dn_sh = np.minimum(o, c) - lo
    pin = ((up_sh > body * 2) & (dn_sh < body)) | ((dn_sh > body * 2) & (up_sh < body))
    shape = doji | hammer | pin
    green, red = c > o, c < o
    x_up = (c > h.shift(1)) & (c.shift(1) <= h.shift(2))
    x_dn = (c < lo.shift(1)) & (c.shift(1) >= lo.shift(2))
    brk_up = x_up & green.shift(1, fill_value=False)
    brk_dn = x_dn & red.shift(1, fill_value=False)
    le = (green & brk_up.shift(1, fill_value=False)) | (shape & x_up)
    se = (red & brk_dn.shift(1, fill_value=False)) | (shape & x_dn)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
