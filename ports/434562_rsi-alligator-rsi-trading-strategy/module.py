"""RSI "alligator" crosses, broker days: the RSI 13 crossing above the RSI 34 with the RSI 5 above it, or the RSI 5 crossing
above the RSI 34 with the RSI 13 above it, goes long; the mirror crosses go short (reversing). Longs carry a 10 % stop and
a 90 % target; shorts have no bracket.
Port of FMZ strategy #434562 "RSI鳄鱼交易策略Alligator-RSI-Trading-Strategy" (RSI Alligator).

FMZ source id: 434562

Source
    https://www.fmz.com/strategy/434562 (PineScript v3, FMZ last modified 2023-12-07 15:46:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 133-165), RSI 34 / 5 / 13 (jaws / teeth / lips); long SL 10 %, TP 90 % of the average price
    crossover(rsi13, rsi34) and rsi5 > rsi34 or crossover(rsi5, rsi34) and rsi13 > rsi34 -> entry long;  mirror crosses -> entry short
    exit("Stop Loss/Profit", "Long", stop = avg (1 - 10 %), limit = avg (1 + 90 %))   (longs only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket uses the fill price, so it is fixed at entry: sl_stop 0.10, tp_stop 0.90 on longs
      only (side-dependent, from the signal); Pine arms it from the bar after the fill (approximation
      stated). Wilder RSIs. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed at entry.
    2 generic: PASS, RSI crosses and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434562_rsi_alligator_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "jaw": [34, 21],
    "sl_pct": [0.10, 0.05],
}
DEFAULT_PARAMS = {"jaw": 34, "teeth": 5, "lips": 13, "sl_pct": 0.10, "tp_pct": 0.90}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())


def _signals(bars_df, p):
    c = bars_df["close"]
    j, t, l_ = _rsi(c, int(p["jaw"])), _rsi(c, int(p["teeth"])), _rsi(c, int(p["lips"]))
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    le = (xo(l_, j) & (t > j)) | (xo(t, j) & (l_ > j))
    se = (xo(j, l_) & (t < j)) | (xo(j, t) & (l_ < j))
    se = se.to_numpy()
    return le.to_numpy() & ~se, se          # both on one bar: the short entries are issued last


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _ = _signals(bars_df, p)
    ix = bars_df.index
    sl = pd.Series(np.where(le, float(p["sl_pct"]), np.nan), index=ix)
    tp = pd.Series(np.where(le, float(p["tp_pct"]), np.nan), index=ix)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
