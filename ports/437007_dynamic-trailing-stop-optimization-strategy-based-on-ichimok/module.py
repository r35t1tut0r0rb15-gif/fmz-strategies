"""Inverse Fisher stochastic crossings with a dynamic tick trailing stop, broker days: the inverse-Fisher transform of a 4-bar WMA of the 19-bar stochastic crossing over 19 goes long, crossing under 82.05 goes
short, reversing; the author's trailing stop (activation and offset in ticks from ATR-derived values) is described, not emitted.
Port of FMZ strategy #437007 "Dynamic Trailing Stop Optimization Strategy Based on Ichimoku Cloud" (IFTS+TS Strategy Overlay).

FMZ source id: 437007

Source
    https://www.fmz.com/strategy/437007 (PineScript v4, FMZ last modified 2023-12-29 14:40:47).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 146-354), stoch & ATR length 19, smooth 4, levels 82.05 / 19; trailing stop on, dynamic start x 68.3, dynamic offset x 1, occurrence 1; re-entry off
    v1 = 0.1 (stoch(close, high, low, 19) - 50);  v2 = wma(v1, 4);  k = (exp(2 v2) - 1) / (exp(2 v2) + 1) x 50 + 50 (same resolution)
    buy = crossover(k, 19) -> entry BUY;  sell = crossunder(k, 82.05) -> entry SELL;  exit(trail_points = dtsiv, trail_offset = dtsov) for both

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing stop (the last of the four exits with the same id wins, with both dynamic switches on):
      activation trail_points = dtsiv ticks, dtsiv = valuewhen(long or short, rsi(atr(19), 19) / 68.3 x 245,
      1), the value at the second-latest signal; offset trail_offset = dtsov ticks, dtsov =
      valuewhen(long or short, sma(atr(19) of 1-MINUTE bars (security "1", lookahead on), 2) x 100, 1). Both
      are tick counts of RSI-of-ATR and 1-minute-ATR quantities: the trail spec cannot express them, so it
      is kept pending (rule 2, mark trailing_stop_pending) and positions end only at the opposite entry
      until the project decides. The Hull lines, levels and labels are plotted only; re-entry is off. REVERSAL
      INTENDED. The 100 % of equity size is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, stochastic levels; the tick trail is pending.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, commission and the trailing inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437007_inverse_fisher_stoch_cross"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_len": [19, 14],
    "wma_len": [4, 6],
}
DEFAULT_PARAMS = {"stoch_len": 19, "wma_len": 4, "ul": 82.05, "dl": 19.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    v2 = _wma(0.1 * (st - 50), int(p["wma_len"]))
    e2 = np.exp(2 * v2)
    k = (e2 - 1) / (e2 + 1) * 50 + 50
    k1 = k.shift(1)
    ul, dl = float(p["ul"]), float(p["dl"])
    buy = (k > dl) & (k1 <= dl)
    sell = (k < ul) & (k1 >= ul)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
