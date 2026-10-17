"""Closes beyond the 44-bar EMA of highs (lows) in the EMA 200 trend, with the opposite EMA band as the stop, daily
(broker-day) bars: a close above EMA(high, 44) and above EMA 200 goes long with its stop at EMA(low, 44); a close below
EMA(low, 44) and below EMA 200 goes short with its stop at EMA(high, 44).
Port of FMZ strategy #483503 "动态双均线趋势跟踪策略-Dynamic-Dual-EMA-Trend-Following-Strategy" (RENTABLE Dual EMA Breakout TSLA).

FMZ source id: 483503

Source
    https://www.fmz.com/strategy/483503 (PineScript v5, FMZ last modified 2025-02-27 16:50:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 95-139), EMA 44 of highs / lows, EMA 200 filter on, direction Both
    long = close > ema(high, 44) and close > ema200; short = close < ema(low, 44) and close < ema200
    exit(stop = ema(low, 44)) for the long, exit(stop = ema(high, 44)) for the short, on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are re-issued on every bar at the CURRENT band (a moving level): fixed at the entry as the signal
      bar's distance ((close - ema(low, 44)) / close for a long, (ema(high, 44) - close) / close for a short), picked by
      the signal's side, shifted one bar inside stops() and re-based on the fill; mark trailing_stop_pending. A signal
      whose stop is already on the wrong side of the close (zero-length trade) emits no entry (as #490798).
    * The risk-based qty (1 % of equity over the stop distance) is sizing: not ported. Every bar in the condition is
      an entry signal (same-side ignored while held). Trade direction Both / Long is a GRID variant.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York) stamped with their first minute (as #430984); stops on daily bars: coarse_bar_stop.
      FREQ = "1D" from the backtest header ("TSLA" and the 1-4 h comment are labels).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, EMAs of highs, lows and closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based qty is quoted in original_sizing.txt and not ported; the stop via stops().
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483503_ema_high_low_band_breakout_band_stop"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [44, 22],
    "direction": ["Both", "Long"],
}
DEFAULT_PARAMS = {"length": 44, "trend_len": 200, "use_filter": True, "direction": "Both"}


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
    n = int(p["length"])
    eh, el = h.ewm(span=n, adjust=False).mean(), lo.ewm(span=n, adjust=False).mean()
    trend = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    d_long, d_short = (c - el) / c, (eh - c) / c
    up_ok = (c > trend) if p["use_filter"] else True
    dn_ok = (c < trend) if p["use_filter"] else True
    long_e = ((c > eh) & up_ok & (d_long > 0)).astype(bool)
    short_e = ((c < el) & dn_ok & (d_short > 0)).astype(bool)
    if p["direction"] == "Long":
        short_e = pd.Series(False, index=c.index)
    elif p["direction"] == "Short":
        long_e = pd.Series(False, index=c.index)
    return long_e, short_e, d_long, d_short


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, d_long, d_short = _signals(bars_df, p)
    return {"sl_stop": d_long.where(long_e, d_short).shift(1)}


def portfolio_kwargs(**params):
    return {}
