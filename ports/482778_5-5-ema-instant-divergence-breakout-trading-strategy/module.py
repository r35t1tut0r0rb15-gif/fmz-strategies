"""Bars wholly below or above the EMA 5, broker days: a bar wholly below goes long with its stop at the bar's low and a target 3 bar-ranges over its high; a bar wholly above goes short with its stop at the bar's high and a target 3 ranges under its low; reversing.
Port of FMZ strategy #482778 "5均线即时背离突破交易策略-5-EMA-Instant-Divergence-Breakout-Trading-Strategy" (5 EMA (Instant Execution)).

FMZ source id: 482778

Source
    https://www.fmz.com/strategy/482778 (PineScript v5, FMZ last modified 2025-02-27 17:50:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-161), EMA 5; target multiplier 3.0; margin 100 / 100
    high < ema5 and low < ema5 -> trigger_high := high;  high > ema5 and low > ema5 -> trigger_low := low
    high >= trigger_high -> entry Long + exit(limit = trigger_high + 3 (trigger_high - low), stop = low), trigger_high := na;  low <= trigger_low -> entry Short + exit (mirror), trigger_low := na

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trigger is set from the same bar it is tested on, so high >= trigger_high holds at once: every bar
      wholly below the EMA signals a long at its close (and the trigger is cleared), every bar wholly above
      a short, as written. The levels are fixed at the signal bar and sent as fractions of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256). Runs of such bars repeat
      the signal while the side is held, re-sending the bracket from the new bar; stops() keeps the first,
      so the repeat case is marked trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The margin settings are
      not sizing signals. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar range bracket as fractions of the fill.
    2 generic: PASS, bars beyond the EMA 5 with a range bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin 100 / 100 stored, not ported.
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

NAME = "fmz_482778_bar_beyond_ema5_range_3x_bracket_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_length": [5, 10],
    "target_multiplier": [3.0, 1.5],
}
DEFAULT_PARAMS = {"ema_length": 5, "target_multiplier": 3.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    le = (h < e) & (lo < e)
    se = (h > e) & (lo > e)
    k = float(p["target_multiplier"])
    rng = h - lo
    lvl = {"l_sl": lo, "l_tp": h + rng * k, "s_sl": h, "s_tp": lo - rng * k}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
