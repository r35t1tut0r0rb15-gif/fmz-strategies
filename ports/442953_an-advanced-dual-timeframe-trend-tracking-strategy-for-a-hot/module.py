"""Daily and hourly EMA 20 / 50 agreement, daily bars: the daily EMA 20 above the EMA 50 with the hourly EMA 20 above its EMA 50 (the day's last hourly value) holds long, both below holds short; the ATR
bracket re-sent while the signal holds is described and kept pending; reversing.
Port of FMZ strategy #442953 "An Advanced Dual Timeframe Trend Tracking Strategy for a Hot Stock" (TSLA Enhanced Trend Master 2023).

FMZ source id: 442953

Source
    https://www.fmz.com/strategy/442953 (PineScript v5, FMZ last modified 2024-02-27 16:01:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-171), EMA 20 / 50 daily and on 60 minutes; year 2023 only (dropped); ATR 14 stop 1.5 / target 3; size equity x 2 / close
    buy = 2023 and ema20 > ema50 and ema20_hourly > ema50_hourly -> entry Buy (qty), exit(stop = close - 1.5 atr, limit = close + 3 atr)
    sell = 2023 and both below and shortTradeCount < 0.5 highest(close, 14) -> entry Sell, exit(stop = close + 1.5 atr, limit = close - 3 atr), shortTradeCount + 1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 60-minute request from a daily chart is a lower time frame: its value is the day's last
      hourly bar (as #436765), built from minutes in precompute. The 2023 window is an author date
      window and is dropped. The short count is compared with half the 14-day highest close, a price:
      at the BTC reading it never binds, and it is not ported. The bracket is re-sent on every bar the
      (level) signal holds, from that bar's close and ATR, so it moves while the signal lasts: kept
      pending (mark trailing_stop_pending, as #442117); positions end at the opposite signal until then.
      The equity-based quantity is sizing. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the hourly values end with the day; the re-sent bracket pending.
    2 generic: PASS, daily and hourly EMA agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND442953 (2 members, best partner #443092, Jaccard 0.799); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442953_daily_hourly_ema20_50_agreement_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    c60 = df["close"].resample("1h", label="left", closed="left").last().dropna()
    d60 = broker_day(c60.index)
    for col, n in (("ema_f_h", int(p["fast"])), ("ema_s_h", int(p["slow"]))):
        e = c60.ewm(span=n, adjust=False).mean()
        bars[col] = e.groupby(d60).last().reindex(bars.index).to_numpy()   # the day's last hourly value
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    hf, hs = bars_df["ema_f_h"], bars_df["ema_s_h"]
    le = (ef > es) & (hf > hs)
    se = (ef < es) & (hf < hs)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
