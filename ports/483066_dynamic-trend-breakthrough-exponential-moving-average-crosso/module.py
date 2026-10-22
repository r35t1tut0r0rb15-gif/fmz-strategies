"""EMA 33 crossings with 14-bar swing brackets, broker days: the close crossing over the EMA goes long (target the 14-bar high, stop the 14-bar low), a close under the EMA goes short (target the 14-bar low, stop the 14-bar high); reversing.
Port of FMZ strategy #483066 "Dynamic Trend Breakthrough Exponential Moving Average Crossover Strategy" (33 EMA Crossover Strategy).

FMZ source id: 483066

Source
    https://www.fmz.com/strategy/483066 (PineScript v6, FMZ last modified 2025-02-27 17:05:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-135), EMA 33; swing high / low over 14 bars; MPL 2.0 notice (GlenMabasa)
    crossover(close, ema33) and close > ema33 -> entry Buy + exit(limit = highest(high, 14), stop = lowest(low, 14))
    crossunder(close, ema33) or close < ema33 -> entry Sell + exit(limit = lowest(low, 14), stop = highest(high, 14))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing levels include the signal bar, as written. The sell condition is a state that repeats on
      every bar under the EMA, each repeat re-sending the bracket from the new swing levels; the port
      fixes the bracket at the opening signal bar and sends it as fractions of the fill open (a level at
      or through it is marketable and closed one bar late, as #458256), mark trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. The MPL 2.0 notice is kept
      with the verbatim copy (ported, stated). Near-duplicate of #482870 (ND482870; the same rules with EMA 22), ported under rule 7.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with swing brackets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND482870 (2 members, best partner #482870, Jaccard 0.746); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483066_ema33_cross_swing14_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_length": [33, 22],
    "swing_length": [14, 7],
}
DEFAULT_PARAMS = {"ema_length": 33, "swing_length": 14}


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
    se = ((c < e) & (c.shift(1) >= e.shift(1))) | (c < e)
    le = (c > e) & (c.shift(1) <= e.shift(1)) & ~se
    n = int(p["swing_length"])
    sh, sl = h.rolling(n).max(), lo.rolling(n).min()
    lvl = {"l_sl": sl, "l_tp": sh, "s_sl": sh, "s_tp": sl}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
