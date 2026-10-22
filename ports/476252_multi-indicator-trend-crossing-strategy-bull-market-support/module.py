"""Weekly SMA 20 / EMA 21 crossings (the bull-market support band) from completed broker weeks, broker days, long only: the SMA crossing over the EMA buys, crossing under closes.
Port of FMZ strategy #476252 "Multi Indicator Trend Crossing Strategy Bull Market Support Band Trading System" (Demo GPT - Bull Market Support Band).

FMZ source id: 476252

Source
    https://www.fmz.com/strategy/476252 (PineScript v6, FMZ last modified 2024-12-27 14:35:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-158), weekly SMA 20 / EMA 21 of the close; gaps_on, lookahead_off; 100 % of equity; commission 0.1 %, slippage 3
    outSma = security("W", sma(close, 20), gaps_on, lookahead_off);  outEma = security("W", ema(close, 21), same);  crossover(outSma, outEma) -> entry Long;  crossunder -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-6 security() without lookahead is read as the last completed higher bar (as #437508): the
      SMA 20 and EMA 21 of weekly closes as of the previous broker week (a broker week runs Monday to
      Friday by broker-day label), built from the module's own bars. gaps_on is not followed: on
      TradingView it leaves na between the weekly updates, so a crossover test against the previous chart
      bar could never be true; the port compares consecutive weekly values, which is the crossing the
      script plots and names. The date-range inputs always pass. Long only. The 100 % of equity size is
      sizing; the commission and slippage settings are costs and are not ported (house cost model). Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, weekly SMA / EMA band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported; commission / slippage not ported.
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

NAME = "fmz_476252_weekly_sma20_ema21_band_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [20, 10],
    "ema_length": [21, 30],
}
DEFAULT_PARAMS = {"sma_length": 20, "ema_length": 21}


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
    day = broker_day(c.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wc = c.groupby(week).last()
    w_sma = wc.rolling(int(p["sma_length"])).mean()
    w_ema = wc.ewm(span=int(p["ema_length"]), adjust=False).mean()
    a = pd.Series(w_sma.shift(1).reindex(week).to_numpy(), index=c.index)   # last completed week
    b = pd.Series(w_ema.shift(1).reindex(week).to_numpy(), index=c.index)
    le = (a > b) & (a.shift(1) <= b.shift(1))
    lx = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
