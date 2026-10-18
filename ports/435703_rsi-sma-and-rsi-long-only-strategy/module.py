"""Close over its SMA, broker days, long only: the close crossing over the SMA 14 goes long; the long is closed by the RSI 14 crossing
under 70, the RSI over 75, the close crossing under the SMA 7 of lows, or the close crossing under the SMA 14.
Port of FMZ strategy #435703 "基于均线和RSI的单边多头策略SMA-and-RSI-Long-Only-Strategy" (MAs & RSI strategy long only).

FMZ source id: 435703

Source
    https://www.fmz.com/strategy/435703 (PineScript v4, FMZ last modified 2023-12-18 10:28:10).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 152-179), SMA 14 (fast and long), SMA 7 of lows (stop), RSI 14, levels 70 / 75
    entry long: crossover(close, sma(close, 14));  close long on any of: crossunder(rsi, 70), rsi > 75, crossunder(close, sma(low, 7)), crossunder(close, sma(close, 14))

Interpretation choices (Pine rules in SURVEY_README.md)
    * An entry bar that also meets an exit (the RSI over 75 on the cross bar) sends the entry and
      then the close: the position ends flat, so that entry signal is dropped. Long only. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average and RSI rules.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435703_sma_rsi_long_only"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emapl": [14, 20],
    "rsi_period": [14, 7],
}
DEFAULT_PARAMS = {"emapf": 14, "emapl": 14, "emaps": 7, "rsi_period": 14}


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
    lo, c = bars_df["low"], bars_df["close"]
    maf = c.rolling(int(p["emapf"])).mean()
    mal = c.rolling(int(p["emapl"])).mean()
    masl = lo.rolling(int(p["emaps"])).mean()
    n = int(p["rsi_period"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    entry = (c > mal) & (c.shift(1) <= mal.shift(1))
    exit_ = (((rsi < 70) & (rsi.shift(1) >= 70)) | (rsi > 75)
             | ((c < masl) & (c.shift(1) >= masl.shift(1)))
             | ((c < maf) & (c.shift(1) >= maf.shift(1))))
    entry, exit_ = entry.fillna(False), exit_.fillna(False)
    false = pd.Series(False, index=bars_df.index)
    return (entry & ~exit_).astype(bool), exit_.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
