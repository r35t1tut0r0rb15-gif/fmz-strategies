"""Bars entirely below the EMA 5 go long with the stop at the bar's low and a target 3 bar ranges above its high;
bars entirely above go short (mirrored), daily bars.
Port of FMZ strategy #482778 "5均线即时背离突破交易策略-5-EMA-Instant-Divergence-Breakout-Trading-Strategy" (5 EMA (Instant Execution)).

FMZ source id: 482778

Source
    https://www.fmz.com/strategy/482778 (PineScript v5, FMZ last modified 2025-02-27 17:50:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 114-150), EMA 5, target x 3
    high < ema and low < ema -> trigger_high := high; buy = high >= trigger_high
    buy -> entry long with exit(limit = trigger_high + 3 (trigger_high - low), stop = low); trigger reset
    (short mirrored with low > ema, trigger_low := low)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trigger is set from the bar's own high and tested against the same high, so every bar entirely below the
      EMA is a buy at once (the "instant execution" of the title); a stored trigger cannot survive a bar.
    * The bracket is placed with the entry from the signal bar: (close - low) / close and (high + 3 range - close) /
      close for longs, mirrored for shorts, picked by the signal's side, shifted one bar inside stops() and re-based
      on the fill (house rule). A bar closing at its low (high) emits no long (short) (zero-length stop, as L2
      #491035). A later same-side signal while held re-places the bracket: fixed at entry, mark
      trailing_stop_pending (as #491506).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-placed bracket fixed at entry (marked).
    2 generic: PASS, an EMA and the signal bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482778_bar_beyond_ema5_range_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [5, 10],
    "target_mult": [3.0, 1.5],
}
DEFAULT_PARAMS = {"ema_len": 5, "target_mult": 3.0}


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


def _parts(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rng = h - lo
    sl_l, tp_l = (c - lo) / c, (h + p["target_mult"] * rng - c) / c
    sl_s, tp_s = (h - c) / c, (c - (lo - p["target_mult"] * rng)) / c
    long_e = (h < ema) & (lo < ema) & (sl_l > 0)
    short_e = (h > ema) & (lo > ema) & (sl_s > 0)
    return long_e.astype(bool), short_e.astype(bool), sl_l, tp_l, sl_s, tp_s


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _parts(bars_df, p)[:2]
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, sl_l, tp_l, sl_s, tp_s = _parts(bars_df, p)
    sl = sl_l.where(long_e, sl_s)          # picked by the signal's side
    tp = tp_l.where(long_e, tp_s)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
