"""Pivot trendline breaks, reversed as the defaults set it, broker days: lines through the last two confirmed pivot highs
(100 / 15) and pivot lows; a close breaking below the support line goes LONG and above the resistance line goes SHORT;
as written only the short carries the 4 ATR stop and 2 R target.
Port of FMZ strategy #430840 "Trend Line Trading Strategy" (Trendlines Strategy).

FMZ source id: 430840

Source
    https://www.fmz.com/strategy/430840 (PineScript v4, FMZ last modified 2023-11-02 14:14:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 190-425), pivots 100 / 15, ATR stop 14 x 4, target 2 R, reverse trades on, direct reversal on
    resistance = line through the last two pivot highs at bar_index; support = line through the last two pivot lows
    BUY = crossover(close, resistance); SELL = crossunder(close, support)
    reverse on: SELL -> entry long; BUY -> entry short   (direct reversal allowed)
    exit("TP & SL", "long", limit = TP, stop = SL); exit("TP & SL", "short", limit = STP, stop = SSL)   (every bar)
    ATR stop: ohlc4 -/+ 4 atr(14) taken on the bar the position changed; target = avg +/- 2 x the stop distance

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow(100, 15): the bar 15 back is strictly above (below) the 100 bars before it
      and the 15 after it (ties are not pivots); a pivot is known 15 bars after it, so only past bars
      are read. The lines are extrapolated to the current bar from the two latest pivots.
    * Both exits share the id "TP & SL" and are re-issued every bar, the short's last: only shorts are
      bracketed, a long leaves by reversal (as #426300). The source takes the stop from the bar the
      position changes (the fill bar's ohlc4 and ATR); the port takes it from the signal bar (known at
      the fill's open), as fractions of its close shifted one bar (stated approximation).
    * strategy.risk.allow_entry_in with direction 0 allows both sides. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the shared-id bracket read as written (shorts only), levels from the signal bar.
    2 generic: PASS, pivot trendlines, ATR multiples and a reward ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored; the stop options quoted in original_sizing.txt.
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

NAME = "fmz_430840_trendline_breaks_reversed"
FAMILY = "pivot_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "leftbars": [100, 50],
    "rightbars": [15, 10],
}
DEFAULT_PARAMS = {"leftbars": 100, "rightbars": 15, "atr_len": 14, "atr_mult": 4.0, "rr": 2.0}


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


def _pivots(x, lb, rb, high):
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def _line(x, piv, rb):
    """Value at each bar of the line through the last two pivots (as the source's valuewhen pairs)."""
    m = len(x)
    out = np.full(m, np.nan)
    x1 = y1 = x2 = y2 = np.nan
    for t in range(m):
        if piv[t]:
            x2, y2 = x1, y1
            x1, y1 = t - rb, x[t - rb]
        if not np.isnan(x2) and x1 != x2:
            mm = (y2 - y1) / (x2 - x1)
            out[t] = mm * t + (y1 - mm * x1)
    return out


def _signals(bars_df, p):
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    lb, rb = int(p["leftbars"]), int(p["rightbars"])
    res = pd.Series(_line(h, _pivots(h, lb, rb, True), rb), index=bars_df.index)
    sup = pd.Series(_line(lo, _pivots(lo, lb, rb, False), rb), index=bars_df.index)
    cs = bars_df["close"]
    buy = (cs > res) & (cs.shift(1) <= res.shift(1))
    sell = (cs < sup) & (cs.shift(1) >= sup.shift(1))
    long_e = sell.astype(bool)                          # reverse trades (default)
    short_e = (buy & ~sell).astype(bool)
    return long_e, short_e


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, short_e = _signals(bars_df, p)
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"])
    sl_frac = ((o + h + lo + c) / 4 + atr - c) / c
    sl = pd.Series(np.where(short_e & (sl_frac > 0), sl_frac, np.nan), index=bars_df.index)
    tp = sl * float(p["rr"])
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
