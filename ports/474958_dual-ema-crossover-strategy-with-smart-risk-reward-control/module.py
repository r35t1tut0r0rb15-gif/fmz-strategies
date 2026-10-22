"""EMA 15 / 50 crossings, daily bars: the cross up goes long with a stop at the lower of the two previous opens and a 2 R target from the signal close; the cross down goes short with the mirror; reversing.
Port of FMZ strategy #474958 "Dual EMA Crossover Strategy with Smart Risk Reward Control" (EMA Cross - Any Direction).

FMZ source id: 474958

Source
    https://www.fmz.com/strategy/474958 (PineScript v5, FMZ last modified 2024-12-13 10:30:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-129), EMA 15 / 50; stop = lowest / highest of open[1] over 2 bars; target 2 R; 30 % of equity
    crossover -> entry Long, exit(stop = lowest(open[1], 2), limit = close + 2 (close - stop));  crossunder -> entry Short, exit(stop = highest(open[1], 2), limit = close - 2 (stop - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar: sent as fractions of the fill open; a level at or
      through it is marketable and closed one bar late (as #458256). Crossings alternate, so no repeat
      signal re-sends it. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. The equity share is not ported. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with a previous-opens stop and a 2 R target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474958_ema15_50_cross_prev_opens_stop_2r_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [15, 10],
    "long_len": [50, 100],
}
DEFAULT_PARAMS = {"short_len": 15, "long_len": 50}


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
    o, c = bars_df["open"], bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    o1 = o.shift(1)
    l_sl, s_sl = o1.rolling(2).min(), o1.rolling(2).max()
    lvl = {"l_sl": l_sl, "l_tp": c + 2 * (c - l_sl), "s_sl": s_sl, "s_tp": c - 2 * (s_sl - c)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


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
