"""Close crossings of the Supertrend line (ATR 10 x 3), daily bars: the close crossing over the line goes long, crossing under goes short, each with a 1 % target and 1 % stop; reversing.
Port of FMZ strategy #458069 "Precision Trading Strategy and Risk Management System Based on SuperTrend Indicator" (Supertrend Strategy with 1% Target and 1% Stop Loss).

FMZ source id: 458069

Source
    https://www.fmz.com/strategy/458069 (PineScript v5, FMZ last modified 2024-07-29 16:58:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 184-224), ta.supertrend(3, 10); target 1 %, stop 1 % of the signal close
    crossover(close, supertrend) -> entry Long + exit(limit = close x 1.01, stop = close x 0.99);  crossunder -> entry Short + exit(limit = close x 0.99, stop = close x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's built-in supertrend. The bracket is sent once on the signal bar from its close: ported as
      the fixed fraction 0.01 of the fill. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the percent bracket as fixed fractions.
    2 generic: PASS, Supertrend line crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458069_supertrend_line_cross_1pct_bracket_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_len": [10, 14],
    "factor": [3.0, 2.0],
    "bracket": [0.01, 0.03],
}
DEFAULT_PARAMS = {"atr_len": 10, "factor": 3.0, "bracket": 0.01}


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


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): (direction -1 up / 1 down, line)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr, st


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    _, st = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_len"]))
    st = pd.Series(st, index=c.index)
    le = (c > st) & (c.shift(1) <= st.shift(1))
    se = (c < st) & (c.shift(1) >= st.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    b = float(p["bracket"])
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
