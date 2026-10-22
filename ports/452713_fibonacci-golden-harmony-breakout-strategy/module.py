"""Re-crosses of the last EMA 9 / 21 cross-up close, daily bars: the 'golden pocket' level collapses to the close of the latest EMA cross up (high = low there), and the close crossing over it goes long, crossing under it goes short; reversing.
Port of FMZ strategy #452713 "Fibonacci Golden Harmony Breakout Strategy" (Golden Pocket Trendline Breakout Strategy).

FMZ source id: 452713

Source
    https://www.fmz.com/strategy/452713 (PineScript v5, FMZ last modified 2024-05-28 13:56:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-146), EMA 9 / 21; fib 0.618 of the var high / low (both the cross-up close)
    crossover(ema9, ema21) -> low = high = close (from na);  crossunder -> low = high = na;  fib_618 = high - (high - low) x 0.618 while both set (kept when they are na)
    close > fib_618 and crossover(close, fib_618) -> entry Buy;  close < fib_618 and crossunder(close, fib_618) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The var low / high are reset to na on every cross down, so each cross up sets both to that
      bar's close and the 0.618 level equals it; the level is not cleared on the cross down (it is
      only recomputed while both are set), so it holds the latest cross-up close. The entries are
      crossings of the close with that level (on the cross-up bar itself the close equals it, so no
      entry). REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, re-crosses of the last cross-up close.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452713_ema9_21_crossup_close_level_recross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [21, 26],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    fib = np.full(m, np.nan)
    lo_v = hi_v = fv = np.nan
    for i in range(m):
        if up[i]:
            lo_v = cv[i] if np.isnan(lo_v) else min(lo_v, cv[i])
            hi_v = cv[i] if np.isnan(hi_v) else max(hi_v, cv[i])
        elif dn[i]:
            lo_v = hi_v = np.nan
        if not np.isnan(lo_v) and not np.isnan(hi_v):
            fv = hi_v - (hi_v - lo_v) * 0.618
        fib[i] = fv
    fb = pd.Series(fib, index=c.index)
    c1, f1 = c.shift(1), fb.shift(1)
    le = (c > fb) & (c1 <= f1)
    se = (c < fb) & (c1 >= f1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
