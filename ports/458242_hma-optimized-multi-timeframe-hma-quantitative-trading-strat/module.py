"""Hull 55 turns, daily bars, long only: the Hull average crossing over its value 2 bars back buys with a one-tick trailing stop that starts after one tick of profit; the cross back under closes the long (short entries are not allowed).
Port of FMZ strategy #458242 "HMA优化多周期量化交易策略与动态止损结合-Optimized-Multi-Timeframe-HMA-Quantitative-Trading-Strategy-with-Dynamic-Stop-Loss" (DAP Hull Sweet Scalp v1 Strategy).

FMZ source id: 458242

Source
    https://www.fmz.com/strategy/458242 (PineScript v5, FMZ last modified 2024-07-31 11:28:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-250), HMA 55 (WMA 27 / 55, WMA 7); session 1800-1700 (flat at its end); direction 'long'; trail_points 1, trail_offset 1 tick
    in session and crossover(hull, hull[2]) -> entry long + exit(trail_points = 1, trail_offset = 1);  in session and crossunder -> entry short (+ trail)
    end of session -> close_all;  strategy.risk.allow_entry_in(long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With allow_entry_in(long) a short entry only closes the long, so the cross under is the long's
      exit. The 18:00-17:00 session covers every daily bar's open time (the daily bars start inside it),
      so the session test always holds and its end never comes on daily bars. _length / 2 = 27.5 is
      read as the integer 27 for the WMA, round(sqrt(55)) = 7. The trail of 1 tick after 1 tick of profit
      is 0.1 in price: read as the house percent trail 0.1 / 42000 behind the best price, active after
      the same gain (anchor high_low; mark trailing_stop). Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: PASS, Hull average turns with a tight trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 1800-1700 holds on every daily bar (not applied).
Long only.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458242_hull55_turn_one_tick_trail_long"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [55, 180],
    "trail_pct": [0.0000024, 0.01],
}
DEFAULT_PARAMS = {"length": 55, "trail_pct": 0.0000024}


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
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    h2 = hull.shift(2)
    le = (hull > h2) & (hull.shift(1) <= h2.shift(1))
    lx = (hull < h2) & (hull.shift(1) >= h2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = float(p["trail_pct"])
    return {"trail": {"type": "percent", "pct": t, "anchor": "high_low", "activate_after": t}}


def portfolio_kwargs(**params):
    return {}
