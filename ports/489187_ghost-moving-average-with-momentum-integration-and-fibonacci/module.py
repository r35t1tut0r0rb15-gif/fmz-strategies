"""Close crossings of a Hull-type "ghost" MA 20 with the sign of the smoothed 20-bar momentum, 3-day bars: the up-cross with positive momentum goes long, the down-cross with negative momentum goes short, with a target 0.618 and a stop 0.382 of the 50-bar range from the signal close; reversing.
Port of FMZ strategy #489187 "Ghost Moving Average with Momentum Integration and Fibonacci Target Stop Loss Strategy" (Ghost MA + Momentum + Fib TP/SL + Dashboard).

FMZ source id: 489187

Source
    https://www.fmz.com/strategy/489187 (PineScript v5, FMZ last modified 2025-04-02 15:33:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-228), GMA 20 (wma(2 wma(10) - wma(20), 4)); momentum 20, EMA 10, / stdev 20; swing 50; TP 0.618, SL 0.382 of the range; 10 % of equity
    crossover(close, gma) and ema(close - close[20], 10) / stdev(...) > 0 -> entry Long + exit(limit = close + 0.618 range, stop = close - 0.382 range);  mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ghost MA is wma(2 x wma(close, 10) - wma(close, 20), round(sqrt(20)) = 4). The bracket is set on
      the signal bar from its close and the 50-bar high-low range (signal bar included) and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A later same-side crossing while held re-sends the bracket; the port keeps the opening
      levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. Bars are blocks of three broker days (17:00 America/New_York) counted from
      1970-01-01, stamped with their first minute. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; range bracket as fractions of the fill.
    2 generic: PASS, Hull-type MA crossings with momentum and a Fibonacci-range bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: three-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489187_ghost_ma20_cross_momentum_fib_range_bracket_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (three broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "gmaLength": [20, 50],
    "swingLookback": [50, 20],
}
DEFAULT_PARAMS = {"gmaLength": 20, "swingLookback": 50, "momentumLength": 20, "momentumSmoothing": 10, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: a @ w / w.sum(), raw=True)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["gmaLength"])
    gma = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    k = int(p["momentumLength"])
    mom = c - c.shift(k)
    sd = mom.rolling(k).std(ddof=0)
    nm = mom.ewm(span=int(p["momentumSmoothing"]), adjust=False).mean() / sd.where(sd > 0)
    le = (c > gma) & (c.shift(1) <= gma.shift(1)) & (nm > 0)
    se = (c < gma) & (c.shift(1) >= gma.shift(1)) & (nm < 0)
    sw = int(p["swingLookback"])
    rng = h.rolling(sw).max() - lo.rolling(sw).min()
    lvl = {"l_sl": c - rng * 0.382, "l_tp": c + rng * 0.618, "s_sl": c + rng * 0.382, "s_tp": c - rng * 0.618}
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
