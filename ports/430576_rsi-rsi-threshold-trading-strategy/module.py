"""RSI 10 dip, broker days, long only: RSI 10 under 30 goes long; RSI 10 over 40, or the tenth bar after the last dip
signal, closes the long.
Port of FMZ strategy #430576 "基于RSI的阈值交易策略RSI-Threshold-Trading-Strategy" (Simple RSI Buy/Sell at a level).

FMZ source id: 430576

Source
    https://www.fmz.com/strategy/430576 (PineScript v4, FMZ last modified 2023-10-30 14:58:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-213), RSI 10, oversold 30, overbought 40, 10-bar time exit
    myEntry = rsi(close, 10) < 30 and hour(time) <= 9 -> entry long
    barssince(myEntry) >= 10 or rsi(close, 10) > 40 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the 1-day header chart every bar's time is the session start (hour 0), so hour(time) <= 9
      always holds: the filter is vacuous at the source's bar size and is not ported (no clock rule
      remains; skill section 5 / check 9 not engaged).
    * The time exit is an explicit exit signal 10 bars after the last bar with the entry condition
      (it restarts while RSI stays under 30), not max_hold_time. Entry and exit tests exclude each
      other.
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      testPeriod() is always true. Long only; Opposite entries cannot occur. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the time exit as a signal.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out cash order size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the hour filter is vacuous on daily bars.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430576_rsi10_dip_time_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [30, 20],
    "exit_bars": [10, 5],
}
DEFAULT_PARAMS = {"rsi_len": 10, "oversold": 30, "overbought": 40, "exit_bars": 10}


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
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    ent = (r < p["oversold"]).to_numpy()
    since = np.full(len(ent), np.inf)
    last = -1
    for i in range(len(ent)):
        if ent[i]:
            last = i
        if last >= 0:
            since[i] = i - last
    ex = (since >= int(p["exit_bars"])) | (r > p["overbought"]).to_numpy()
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(ent, index=idx), pd.Series(ex & ~ent, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
