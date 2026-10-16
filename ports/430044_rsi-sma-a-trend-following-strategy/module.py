"""RSI extremes with an SMA 200 filter, broker days: above the SMA 200 an RSI 14 under 45 goes long, below it an RSI over
65 goes short; an RSI over 75 above the SMA, or under 25 below it, closes everything; every position has a 5 % stop.
Port of FMZ strategy #430044 "基于RSI极值与SMA均线过滤的趋势跟踪策略A-Trend-Following-Strategy" (Relative Strength Index Extremes with 200-Day Moving Average Filte).

FMZ source id: 430044

Source
    https://www.fmz.com/strategy/430044 (PineScript v5, FMZ last modified 2023-10-24 14:47:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 173-213), RSI 14 (Wilder), SMA 200, stop 5 %
    Long = rsi < 45 and close > sma200 -> entry long;  Short = rsi > 65 and close < sma200 -> entry short
    strategy.close_all(rsi > 75 and close > sma200 or rsi < 25 and close < sma200)
    strategy.exit('SL', loss = round(5 % x avg price / mintick))   (5 % from the entry price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loss in ticks is 5 % of the average entry price: sl_stop 0.05 of the fill.
    * The two close_all conditions close whichever position is held (both exit arrays). No bar can
      both enter and exit (the RSI and SMA tests exclude each other).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed percentage stop.
    2 generic: PASS, RSI levels, a moving average and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 36,000 cash order size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430044 (2 members, best partner #435127, Jaccard 0.931); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430044_rsi_extremes_sma200_stop"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [14, 7],
    "sl_pct": [5.0, 3.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sma_len": 200, "long_lvl": 45, "long_exit": 75, "short_lvl": 65, "short_exit": 25,
                  "sl_pct": 5.0}


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
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    long_e = ((r < p["long_lvl"]) & (c > sma)).astype(bool)
    short_e = ((r > p["short_lvl"]) & (c < sma)).astype(bool)
    ex = (((r > p["long_exit"]) & (c > sma)) | ((r < p["short_exit"]) & (c < sma))).astype(bool)
    return long_e, ex, short_e, ex.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
