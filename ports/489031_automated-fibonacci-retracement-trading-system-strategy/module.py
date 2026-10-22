"""Close crossings of the 20-bar swing's Fibonacci levels, broker days: crossing up over the 61.8 % level goes long with a 1 % stop and 2 % target, crossing down under the 38.2 % level goes short with the mirror bracket, from the signal close; reversing.
Port of FMZ strategy #489031 "Automated Fibonacci Retracement Trading System Strategy" (Estrategia Fibonacci con Señales).

FMZ source id: 489031

Source
    https://www.fmz.com/strategy/489031 (PineScript v5, FMZ last modified 2025-04-01 13:25:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-203), swing 20; Fib 38.2 / 61.8; SL 1 %, TP 2 %; risk 1 % sizing; capital 100
    crossover(close, fib618) -> entry Long (risk qty) + exit(stop = close x 0.99, limit = close x 1.02);  crossunder(close, fib382) -> entry Short + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing window includes the signal bar, as written. The bracket is set on the signal bar from its
      close and sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256). A later same-side crossing while held re-sends the bracket; the port keeps the
      opening levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. The risk-sized quantity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, Fibonacci level crossings with a percent bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity and capital stored, not ported.
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

NAME = "fmz_489031_fib20_618_382_cross_pct_bracket_reversal"
FAMILY = "fibonacci"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 50],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"lookback": 20, "tp_pct": 2.0}


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
    k = int(p["lookback"])
    hi, low_ = h.rolling(k).max(), lo.rolling(k).min()
    f382 = low_ + (hi - low_) * 0.382
    f618 = low_ + (hi - low_) * 0.618
    le = (c > f618) & (c.shift(1) <= f618.shift(1))
    se = (c < f382) & (c.shift(1) >= f382.shift(1))
    tp = float(p["tp_pct"]) / 100
    sl = tp / 2
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
    return le & ~se, se, lvl


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
