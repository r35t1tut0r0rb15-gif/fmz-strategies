"""EMA 20 / 50 crossings, broker days: the cross up goes long with a target half the signal bar's range above its high, the cross down goes short with the mirror below its low; reversing. The 3 % stop is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #477511 "Multi Level Multi Period EMA Crossover Dynamic Take Profit Optimization Strategy" (EMA Crossover Strategy with Take Profit and Candle Highlighting).

FMZ source id: 477511

Source
    https://www.fmz.com/strategy/477511 (PineScript v5, FMZ last modified 2025-01-06 10:50:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-184), EMA 20 / 50 (200 plotted); TP multipliers 0.5 / 1.0 / 1.5 / 2.0 of the signal bar's range; stop 3 % of the current close
    crossover(ema20, ema50) -> tp_k := high + (high - low) x k, entry Buy;  crossunder -> tp_k := low - (high - low) x k, entry Sell
    every bar: exit(TP1..TP4 from Buy / Sell, limit = tp_k);  exit("Stop Loss", Buy, stop = close x 0.97), exit(Sell, stop = close x 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four target exits each close the whole position (no qty given), so the nearest, TP1, fills
      first and cancels the rest: TP1 is ported, set on the signal bar and sent as a fraction of the fill
      open (a level at or through it is marketable and closed one bar late, as #458256). The crossings
      alternate, so no repeat signal moves it. The stop is re-sent on every bar from that bar's close, so
      its level moves after entry: stops() cannot express a level re-set every bar, so it is described
      here and kept pending (as #438034, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar target as a fraction of the fill; per-bar stop described (pending).
    2 generic: PASS, EMA crossings with a range-multiple target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the target multipliers and stop percentage stored.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477511_ema20_50_cross_range_target_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp1_mult": [0.5, 1.0, 2.0],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"tp1_mult": 0.5, "slow": 50, "fast": 20}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    k = float(p["tp1_mult"])
    lvl = {"l_tp": h + (h - lo) * k, "s_tp": lo - (h - lo) * k}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = lvl["l_tp"].shift(1) <= o     # the target marketable at the fill
    s_thr = lvl["s_tp"].shift(1) >= o
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
