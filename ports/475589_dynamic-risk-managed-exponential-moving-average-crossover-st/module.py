"""EMA 9 / 21 crossings, daily bars, long only: the cross up buys with a 1 % stop and 2 % target from the signal close; the cross down sells.
Port of FMZ strategy #475589 "Dynamic Risk Managed Exponential Moving Average Crossover Strategy" (Bitcoin Exponential Profit Strategy).

FMZ source id: 475589

Source
    https://www.fmz.com/strategy/475589 (PineScript v5, FMZ last modified 2024-12-20 14:08:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-132), EMA 9 / 21; risk 1 %, reward 2; trail_offset close x 0.5 % (no trail_points); risk-based size
    crossover -> entry Long (qty by risk), exit(stop = close x 0.99, limit = close x 1.02, trail_offset = close x 0.005);  crossunder -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_offset without trail_points or trail_price sets no trail (as #441084). The bracket is sent
      once, on the signal bar, from its close: sent as fractions of the fill open; a level at or through
      it is marketable and closed one bar late (as #458256). Crossings alternate, so no repeat signal
      re-sends it. The risk-based size is not ported. Long only. Stop module: portfolio_kwargs {} (driver
      D4). Stops on daily bars: mark coarse_bar_stop. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with a bracket and a cross-down exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based size from equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_475589_ema9_21_cross_1_2pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "risk": 0.01, "reward": 2.0}


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
    c = bars_df["close"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    r = float(p["risk"])
    lvl = {"l_sl": c * (1 - r), "l_tp": c * (1 + float(p["reward"]) * r)}
    return le, dn, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, dn, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    thr = le.shift(1, fill_value=False) & ((lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o))
    false = pd.Series(False, index=bars_df.index)
    return le, (dn | thr) & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, dn, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
