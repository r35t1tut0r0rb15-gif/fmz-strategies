"""Big-body bars, broker days, as written: a green bar whose body is at least 26 / 30 of its range goes long; a red bar
whose body is the whole range (30 / 30) goes short; the position reverses on the opposite bar. The tick bracket is armed
only by a repeated same-side bar inside a trade and is not ported.
Port of FMZ strategy #434466 "动态K线大阳线交易策略Dynamic-Candlestick-Big-Yang-Line-Trading-Strategy" (Manham Big Bar Trading Strategy).

FMZ source id: 434466

Source
    https://www.fmz.com/strategy/434466 (PineScript v4, FMZ last modified 2023-12-06 16:22:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-182), lookback 20 (unused); bullish 26, bearish 30 (body / range x 30); target 37 / stop 24 ticks
    body = abs(close - open) / (high - low) x 30;  close > open and body >= 26 -> entry long, exit(stop = avg - 24 ticks, limit = avg + 37 ticks)
    open > close and body >= 30 -> entry short, exit(stop = avg + 37 ticks, limit = avg - 24 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is called only on a signal bar, with levels from the position's average price,
      which is na until the trade is open: the first signal arms nothing, and a bracket appears only
      when a same-side bar repeats inside the trade (an opposite bar arms the next side from the old
      average). A stop that starts after entry cannot be expressed by stops(): the bracket is not
      ported and the module gets the mark trailing_stop_pending (the intended bracket is owed; its
      24 / 37 ticks would need an ATR re-expression, criterion 2).
    * A bar with no range gives no signal (division by zero is na). The lookback input is unused.
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, body / range ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick bracket quoted in original_sizing.txt.
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

NAME = "fmz_434466_big_body_bar_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bull_th": [26, 20],
    "bear_th": [30, 24],
}
DEFAULT_PARAMS = {"bull_th": 26, "bear_th": 30}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (c - o).abs() / (h - lo).replace(0.0, np.nan) * 30
    bull = ((c > o) & (body >= float(p["bull_th"]))).to_numpy()
    bear = ((o > c) & (body >= float(p["bear_th"]))).to_numpy()
    m = len(bull)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if bull[i]:
            q = 1
        elif bear[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
