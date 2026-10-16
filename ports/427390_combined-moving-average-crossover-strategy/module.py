"""T3 + T3 Fibo + MavilimW, broker days (all three switches on, the defaults): the long state is
close above T3 (8, 0.7) and above MavilimW and T3 Fibo (5, 0.618) above T3; the short state is the
mirror. A position opens on the first bar of a new state run after the opposite state was seen, each
side closes on the opposite state, and a 3 % stop protects each entry.
Port of FMZ strategy #427390 "Combined Moving Average Crossover Strategy".

FMZ source id: 427390

Source
    https://www.fmz.com/strategy/427390 (PineScript v4, FMZ last modified 2023-09-20 16:42:37).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 170-328), stop 3 %, T3 8 / 0.7, T3 Fibo 5 / 0.618, MavilimW 3 / 5
    T3(x) of (high + low + 2 close) / 4; MavilimW = six chained WMAs (3, 5, 8, 13, 21, 34) of close
    long = close > T3 and close > MAVW and T32 > T3; longclose = close < T3 and close < MAVW and T32 < T3
    long_plot = barssince(long[1]) > barssince(longclose[1]) ? long : na (short mirrors)
    entry long on long_plot; close on longclose_plot; exit(stop = avg x (1 - 3 %)) (short mirrors)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With all three switches on (defaults) only the "T3 + Fibo + MAVW" branch is live; the other
      branches are na. barssince of a series that was never true is na (comparison false), as written.
    * The 3 % stop is fixed at entry: sl_stop 0.03 of the fill (stops()); daily bars with a stop:
      mark coarse_bar_stop.
    * Entries are emitted on their signal bars; an opposite entry reverses (REVERSAL INTENDED);
      stop module: portfolio_kwargs {} (driver D4).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is fixed at entry.
    2 generic: PASS, MA lengths and a stop as a fraction of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 75 % of equity stored; the stop ported via stops().
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8). (The T3 "volume factor" is a smoothing constant.)
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427390_t3_fibo_mavilimw"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length1": [8, 13],
    "length12": [5, 3],
    "stop_loss": [3.0, 6.0],
}
DEFAULT_PARAMS = {"length1": 8, "a1": 0.7, "length12": 5, "a12": 0.618, "fmal": 3, "smal": 5, "stop_loss": 3.0}


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


def _t3(x, n, a):
    e = [x.ewm(span=n, adjust=False).mean()]
    for _ in range(5):
        e.append(e[-1].ewm(span=n, adjust=False).mean())
    c1 = -a ** 3
    c2 = 3 * a * a + 3 * a ** 3
    c3 = -6 * a * a - 3 * a - 3 * a ** 3
    c4 = 1 + 3 * a + a ** 3 + 3 * a * a
    return c1 * e[5] + c2 * e[4] + c3 * e[3] + c4 * e[2]


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _bars_since(flag):
    """Pine barssince(flag): bars since flag was last true; nan before it ever was."""
    out = np.full(len(flag), np.nan)
    last = -1
    for i, f in enumerate(flag):
        if f:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _first_of_run(state, close_state):
    s1 = np.concatenate(([False], state[:-1]))
    c1 = np.concatenate(([False], close_state[:-1]))
    bs, bc = _bars_since(s1), _bars_since(c1)
    with np.errstate(invalid="ignore"):
        return state & (bs > bc)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + 2 * c) / 4
    t3 = _t3(src, int(p["length1"]), float(p["a1"]))
    t32 = _t3(src, int(p["length12"]), float(p["a12"]))
    f, s = int(p["fmal"]), int(p["smal"])
    t = f + s
    F = s + t
    Ft = t + F
    S = F + Ft
    mavw = _wma(_wma(_wma(_wma(_wma(_wma(c, f), s), t), F), Ft), S)
    long_s = ((c > t3) & (c > mavw) & (t32 > t3)).to_numpy()
    short_s = ((c < t3) & (c < mavw) & (t32 < t3)).to_numpy()
    long_e = _first_of_run(long_s, short_s)
    long_x = _first_of_run(short_s, long_s)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    # the long close is the first bar of a short run, i.e. the short entry (and the mirror): the closes
    # coincide with the opposite entries, so the entries alone express them (an opposite entry reverses)
    return pd.Series(long_e, index=idx), false.copy(), pd.Series(long_x, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_loss"]) / 100}


def portfolio_kwargs(**params):
    return {}
