"""Broker days, long only: the EMA 20 crossing over the EMA 50 goes long with a target at 1.3 x and a stop at 0.95 x the signal close.
Port of FMZ strategy #474636 "Dynamic Dual EMA Crossover Strategy with Adaptive Profit Loss Control" (TQQQ EMA Strategy (Pineify)).

FMZ source id: 474636

Source
    https://www.fmz.com/strategy/474636 (PineScript v5, FMZ last modified 2024-12-11 11:23:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-305), EMA 20 / 50; TP close x 1.3, SL close x 0.95 per entry
    p_cond_1 = crossover(ema20, ema50) and strategy.equity > 0 -> entry "[n] Entry" (a new id each time), exit("[n] Entry_0", from_entry = that id, limit = close x 1.3, stop = close x 0.95)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each signal gets a new entry id, but default pyramiding allows one long at a time, so a crossover
      while long is refused and its exit (tied to the refused id) never acts; the open trade keeps its
      first bracket. The bracket is sent on the signal bar only, as levels from that close: ported as
      fractions of the fill, exact (1e-6 floor). The time-range and timeframe helpers and the plotting
      flags feed no order; volume is never used. The title names TQQQ; the rules are generic. Long only.
      No sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars:
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, EMA 20 / 50 cross-ups.
    3 crypto-exchange-only: no (exchange pair in the header only (TQQQ named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474636_ema20_50_cross_up_130_95pct_bracket_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_mult": [1.3, 1.15],
    "sl_mult": [0.95, 0.9],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "tp_mult": 1.3, "sl_mult": 0.95}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    buy = (f > s) & (f.shift(1) <= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    lf = le.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - k * float(p["sl_mult"]))
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, k * float(p["tp_mult"]) - 1)
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
