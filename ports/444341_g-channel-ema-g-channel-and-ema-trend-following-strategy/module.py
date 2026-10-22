"""G-Channel trend with an EMA 9 pullback, daily bars, long only: while the latest G-Channel crossing is bullish, a close under the EMA 9 goes long; while it is bearish, a close above the EMA 9 closes.
Port of FMZ strategy #444341 "G-Channel与EMA结合的趋势跟踪策略G-Channel-and-EMA-Trend-Following-Strategy" (G-Channel and EMA Strategy (G-EMA Strategy)).

FMZ source id: 444341

Source
    https://www.fmz.com/strategy/444341 (PineScript v4, FMZ last modified 2024-03-11 11:08:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-146), G-Channel length 100 on close; EMA 9
    a = max(src, nz(a[1])) - nz(a[1] - b[1]) / length;  b = min(src, nz(b[1])) + nz(a[1] - b[1]) / length;  crossup = b[1] < close[1] and b > close;  crossdn = a[1] < close[1] and a > close
    bullish = barssince(crossdn) <= barssince(crossup);  bullish and close < ema -> entry Buy;  not bullish and close > ema -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel follows the script's nz() seeds: on the first bar a = the close and b = min(close, 0)
      (zero on positive prices), as written. barssince() is na until its event has happened, and a
      comparison with na is false, so the state is bearish until both crossings have occurred (as
      #439372). Repeated entries while long are ignored (pyramiding 1). Long only. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, G-Channel state with an EMA pullback.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444341_gchannel_bull_ema9_pullback_long"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "ema_length": [9, 21],
}
DEFAULT_PARAMS = {"length": 100, "ema_length": 9}


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
    cv = c.to_numpy(dtype=float)
    n = float(p["length"])
    m = len(cv)
    a, b = np.zeros(m), np.zeros(m)
    bull = np.zeros(m, dtype=bool)
    last_up = last_dn = -1
    for i in range(m):
        a1 = a[i - 1] if i > 0 else 0.0                # nz(a[1])
        b1 = b[i - 1] if i > 0 else 0.0                # nz(b[1])
        w = (a1 - b1) / n if i > 0 else 0.0            # nz(a[1] - b[1]) / length
        a[i] = max(cv[i], a1) - w
        b[i] = min(cv[i], b1) + w
        if i > 0:
            if b[i - 1] < cv[i - 1] and b[i] > cv[i]:
                last_up = i
            if a[i - 1] < cv[i - 1] and a[i] > cv[i]:
                last_dn = i
        bull[i] = last_up >= 0 and last_dn >= 0 and (i - last_dn) <= (i - last_up)
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean().to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(bull & (cv < e), index=ix), pd.Series(~bull & (cv > e), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
