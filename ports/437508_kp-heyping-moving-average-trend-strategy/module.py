"""Weekly-close EMA against a daily-close EMA, broker days, long only: the EMA 10 of the last completed broker week's close crossing over the EMA 100 of the daily close goes long; crossing under closes it.
Port of FMZ strategy #437508 "KP移动平均趋势策略Heyping-Moving-Average-Trend-Strategy" (KP15).

FMZ source id: 437508

Source
    https://www.fmz.com/strategy/437508 (PineScript v5, FMZ last modified 2024-01-03 12:18:29).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-167), candle frame D, EMA frame W, shifts 0, EMA 10 / 100; log transform off
    ha_close = security(tickerid, "D", close);  mha_close = security(tickerid, "W", close);  fma = ema(mha_close, 10);  sma = ema(ha_close, 100)
    golong = crossover(fma, sma) -> entry Buy;  exitLong = crossunder(fma, sma) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request equals the daily chart. A version-5 security() without lookahead is read as the last
      completed higher bar (SURVEY_README request.security rule): the previous broker week's last close
      (a broker week runs Monday to Friday by broker-day label), built from the module's own bars; the EMA
      10 runs over the daily samples of it. Despite its name the script uses plain closes, not Heikin-Ashi.
      The stop-loss input is unused. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, average crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437508_weekly_close_ema_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fama": [10, 5],
    "sloma": [100, 50],
}
DEFAULT_PARAMS = {"fama": 10, "sloma": 100}


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
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk_close = c.groupby(week).last()
    wclose = pd.Series(wk_close.shift(1).reindex(week).to_numpy(), index=c.index)   # last completed week
    fma = wclose.ewm(span=int(p["fama"]), adjust=False).mean()
    sma = c.ewm(span=int(p["sloma"]), adjust=False).mean()
    up = (fma > sma) & (fma.shift(1) <= sma.shift(1))
    dn = (fma < sma) & (fma.shift(1) >= sma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
