"""EMA 25 / 100 cross-ups, daily bars, long only: the cross up buys with the low of the last red candle under the EMA 100 as stop and a 3 R target from the signal close.
Port of FMZ strategy #475627 "Adaptive EMA Dynamic Position Break out Trading Strategy" (EMA Crossover with TP and SL (Buy only) and Break-even).

FMZ source id: 475627

Source
    https://www.fmz.com/strategy/475627 (PineScript v5, FMZ last modified 2024-12-20 16:33:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-141), EMA 25 / 100; stop = valuewhen(red and close < ema100, low); target close + 3 (close - stop); break-even at +2 % on cross bars
    crossover(ema25, ema100) -> entry Buy, exit(stop = lastRedLow, limit = close + 3 (close - lastRedLow));  on that bar, if long and +2 %: exit(stop = avg)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the cross bar from that bar's values: sent as fractions of the fill open
      (a level at or through it, for example a stop over the close, is marketable and closed one bar
      late, as #458256). The break-even exit and a repeat cross while long (after a cross down, which
      does not close) re-send exits; they are not followed (as #434428, mark trailing_stop_pending).
      Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA cross-ups with a swing stop and 3 R target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_475627_ema25_100_cross_last_red_low_stop_3r_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [25, 10],
    "slow": [100, 50],
}
DEFAULT_PARAMS = {"fast": 25, "slow": 100}


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


def _kept(level, hit):
    """The level of the last bar where `hit` held (na before the first), as a var."""
    v, k = level.to_numpy(dtype=float), hit.to_numpy()
    out = np.full(len(v), np.nan)
    cur = np.nan
    for i in range(len(v)):
        if k[i]:
            cur = v[i]
        out[i] = cur
    return pd.Series(out, index=level.index)


def _signals(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    sl = _kept(lo, (c < o) & (c < b))
    lvl = {"l_sl": sl, "l_tp": c + 3 * (c - sl)}
    return le, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    thr = le.shift(1, fill_value=False) & ((lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o))
    false = pd.Series(False, index=bars_df.index)
    return le, thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
