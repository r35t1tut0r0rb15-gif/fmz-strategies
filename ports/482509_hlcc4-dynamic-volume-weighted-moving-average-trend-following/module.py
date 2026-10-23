"""Broker days, long only: with the close above the weekly VWMA 50 (of the last completed week), two closes in a row above the VWMA 200 with the close above the previous bar's hlcc4 go long; a close under the VWMA 200 closes it, but only while the close is above that weekly VWMA (as written).
Port of FMZ strategy #482509 "动态成交量均线趋势跟踪与HLCC4突破交易策略-Dynamic-Volume-Weighted-Moving-Average-Trend-Following-with-HLCC4-Breakout-Trading-Strategy" (Long-Only 200 WVMA + HLCC4 Strategy (Weekly 50 VWMA Filter, Daily Exit)).

FMZ source id: 482509

Source
    https://www.fmz.com/strategy/482509 (PineScript v6, FMZ last modified 2025-02-18 18:12:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-159), VWMA 200 (daily); weekly VWMA 50 via request.security("W"); hlcc4; 10 % of equity
    above_weekly_vwma = close > request.security("W", vwma(close, 50));  long_condition = close[1] > wvma[1] and close > wvma and close > hlcc4[1]
    if above_weekly_vwma: long_condition and not in_position -> entry Buy;  daily_close < daily_wvma and in_position -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" security calls on the 1-day header chart are the chart's own close and VWMA 200. The
      weekly VWMA 50 (security without lookahead) is read as the value of the last broker week completed
      before the day's own week (weeks labelled by their Monday), as #482904. Both the entry and the exit
      sit inside the weekly filter, so a long is not closed while the close is under the weekly VWMA
      (weird case). in_position mirrors the position (there are no stops). The "last 5 years" window is
      always true. Long only. 10 % of equity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly filter from completed weeks.
    2 generic: PASS, VWMA 200 trend entries above a weekly VWMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day and per broker week) as the VWMA weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); broker weeks for the weekly filter.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482509_vwma200_hlcc4_weekly_vwma50_filter_long_only"
FAMILY = "vwma_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wvma_len": [200, 100],
    "weekly_len": [50, 20],
}
DEFAULT_PARAMS = {"wvma_len": 200, "weekly_len": 50}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _weekly_prev_vwma(bars_df, n):
    """VWMA n of broker-week closes weighted by week volumes (weeks labelled by their Monday), read
    for each day as the value of the last week completed before the day's own week."""
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    wk = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    wc = pd.Series(c.to_numpy(), index=wk).groupby(level=0).last()
    wv = pd.Series(v.to_numpy(), index=wk).groupby(level=0).sum()
    wvma = (wc * wv).rolling(int(n)).mean() / wv.rolling(int(n)).mean()
    prev = wvma.shift(1)                     # the week before each week
    return pd.Series(prev.reindex(wk).to_numpy(), index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["wvma_len"])
    wvma = (c * v).rolling(n).mean() / v.rolling(n).mean()
    hlcc4 = (h + lo + 2 * c) / 4
    above = (c > _weekly_prev_vwma(bars_df, int(p["weekly_len"]))).to_numpy()
    buy = ((c.shift(1) > wvma.shift(1)) & (c > wvma) & (c > hlcc4.shift(1))).to_numpy()
    ex = (c < wvma).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    inpos = False
    for i in range(m):
        if above[i]:
            if buy[i] and not inpos:
                le[i], inpos = True, True
            if ex[i] and inpos:
                lx[i], inpos = True, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
