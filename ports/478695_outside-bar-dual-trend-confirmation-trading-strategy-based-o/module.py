"""Outside bars closing beyond the EMA 5 and the EMA 9 of the bar before, broker days: an outside bar closing above both goes long, below both goes short, each with a stop one bar-height away and a target half a bar-height away from the signal close; reversing.
Port of FMZ strategy #478695 "基于移动平均线和Outside-Bar模式的双重趋势确认交易策略-Dual-Trend-Confirmation-Trading-Strategy-Based-on-Moving-Averages-and-Outside-Bar-Pattern" (Outside Bar EMA Crossover Strategy with EMA Shift).

FMZ source id: 478695

Source
    https://www.fmz.com/strategy/478695 (PineScript v5, FMZ last modified 2025-01-17 14:39:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-169), EMA 5 / 9, EMA 9 shift 1; TP 0.5 x and SL 1.0 x the outside bar's height
    high > high[1] and low < low[1] and close > ema5 and close > ema9[1] -> entry Buy + exit(stop = close - (high - low), limit = close + 0.5 (high - low));  mirror -> entry Sell
    long and close <= close - (high - low) -> close Buy, entry Sell After Buy SL;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close and height: the opening signal's levels are
      ported, sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256); a repeat outside bar inside a trade re-sends it, which is not followed (as
      #434428, mark trailing_stop_pending). The "stop then reverse" test compares the close with the
      CURRENT bar's level, so it holds only on a zero-range bar and is not ported. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, outside bars beyond two EMAs with a bar-height bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_478695_outside_bar_ema5_ema9shift_height_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_ratio": [0.5, 1.0],
    "sl_ratio": [1.0, 0.5],
}
DEFAULT_PARAMS = {"tp_ratio": 0.5, "sl_ratio": 1.0, "ema1": 5, "ema2": 9, "shift": 1}


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
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean().shift(int(p["shift"]))
    outside = (h > h.shift(1)) & (lo < lo.shift(1))
    le = outside & (c > e1) & (c > e2)
    se = outside & (c < e1) & (c < e2)
    ht = h - lo
    tp, sl = float(p["tp_ratio"]), float(p["sl_ratio"])
    lvl = {"l_sl": c - ht * sl, "l_tp": c + ht * tp, "s_sl": c + ht * sl, "s_tp": c - ht * tp}
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
