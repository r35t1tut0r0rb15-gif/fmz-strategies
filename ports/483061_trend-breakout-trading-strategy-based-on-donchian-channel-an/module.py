"""Donchian 20 channel expansions on the SMA 200 side with a stop 45 % of the way from the mid line to the far band,
daily (broker-day) bars: the 20-bar upper band rising above its own previous 20-bar high with the close above SMA 200
goes long; the lower band falling below its previous 20-bar low with the close below SMA 200 goes short.
Port of FMZ strategy #483061 "基于唐奇安通道和移动平均线的趋势突破交易策略-Trend-Breakout-Trading-Strategy-Based-on-Donchian-Channel-and-Moving-Average" (Donchian Channel Strategy with SMA 200 and Custom SL).

FMZ source id: 483061

Source
    https://www.fmz.com/strategy/483061 (PineScript v5, FMZ last modified 2025-02-27 17:07:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 149-183), Donchian 20, SMA 200
    long = upper > highest(upper[1], 20) and close > sma200; short = lower < lowest(lower[1], 20) and close < sma200
    exit(stop = mid - 0.45 (mid - lower)) for the long, (stop = mid + 0.45 (upper - mid)) for the short, every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are re-issued on every bar from the CURRENT channel (a moving level): fixed at the entry as the signal
      bar's distance (close - stop) / close (stop - close for a short), picked by the signal's side, shifted one bar
      inside stops() and re-based on the fill; mark trailing_stop_pending. A signal whose stop is not beyond the close
      emits no entry (as #490798). No target.
    * Every bar in the condition is an entry signal (same-side ignored while held). Entries reverse (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York) stamped
      with their first minute (as #430984); stops on daily bars: coarse_bar_stop. FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, Donchian channels and a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the stop ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483061_donchian_expansion_sma200_mid_stop"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 10],
    "stop_frac": [0.45, 0.9],
}
DEFAULT_PARAMS = {"length": 20, "sma_len": 200, "stop_frac": 0.45}


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
    up, dn = h.rolling(n).max(), lo.rolling(n).min()
    mid = (up + dn) / 2
    sma = c.rolling(int(p["sma_len"])).mean()
    k = p["stop_frac"]
    d_long = (c - (mid - k * (mid - dn))) / c
    d_short = ((mid + k * (up - mid)) - c) / c
    long_e = ((up > up.shift(1).rolling(n).max()) & (c > sma) & (d_long > 0)).astype(bool)
    short_e = ((dn < dn.shift(1).rolling(n).min()) & (c < sma) & (d_short > 0) & ~long_e).astype(bool)
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
