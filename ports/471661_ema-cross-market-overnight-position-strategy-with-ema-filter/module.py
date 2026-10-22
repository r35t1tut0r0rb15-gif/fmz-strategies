"""Alternating one-day longs above a 4-hour EMA 100, daily bars, long only: a flat close over the 4-hour EMA 100 buys, and every long is closed on the next bar's close, so trades last one day and start again from flat.
Port of FMZ strategy #471661 "基于EMA指标的跨市场多空趋势隔夜持仓策略-Cross-Market-Overnight-Position-Strategy-with-EMA-Filter" (Overnight Positioning with EMA Confirmation - Strategy [presentTrading]).

FMZ source id: 471661

Source
    https://www.fmz.com/strategy/471661 (PineScript v5, FMZ last modified 2024-11-12 10:49:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-224), EMA 100 on request.security("240") (a lower time frame on the daily chart); market sessions (US / Asia / Europe) computed but unused by the orders; 10 % of equity; commission 0.02 %, slippage 1
    flat and (close > ema100_4h or not useEMA) -> entry Long;  long -> close Long;  long -> close Long (the Friday force-close, the same test)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session, entry-time and exit-time values (and the Friday test) are computed but no order uses
      them: the entry needs only a flat position and the EMA filter, and every bar that holds a long
      closes it. On daily bars that gives a long bought at one open and sold at the next open, then a new
      entry signal on the bar that ends flat, as written. The "240" request on a daily chart is read as
      the last 4-hour bar completed by the chart bar's close (#436765), built in precompute from the
      minutes. The 3commas messages are alerts only. The costs and the 10 % size are not ported. Long
      only. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; 4-hour values from completed bars.
    2 generic: PASS, one-day longs above a 4-hour EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size, commission and slippage stored, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (computed, unused by the orders).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471661_alternating_one_day_long_above_4h_ema100"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [100, 50],
}
DEFAULT_PARAMS = {"ema_length": 100}


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
    last = pd.Series(df.index, index=df.index).groupby(lab).last()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    h4 = df["close"].resample("4h", label="left", closed="left").last().dropna()
    ema = h4.ewm(span=int(p["ema_length"]), adjust=False).mean().to_numpy()
    h4_end = h4.index.to_numpy().astype("datetime64[ns]") + np.timedelta64(4, "h")
    day_end = last.to_numpy().astype("datetime64[ns]") + np.timedelta64(1, "m")
    k = np.searchsorted(h4_end, day_end, side="right") - 1         # last 4-hour bar completed by the close
    bars["ema_4h"] = np.where(k >= 0, ema[np.clip(k, 0, None)], np.nan)
    return bars


def simulate(bars_df, **params):
    c = bars_df["close"].to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        ok = c > bars_df["ema_4h"].to_numpy(dtype=float)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state = 0                                    # 0 flat, 1 entry sent last bar, 2 exit sent last bar
    for i in range(m):
        if state == 1:
            lx[i], state = True, 2               # the long filled at this open is held: close it
        elif ok[i]:
            le[i], state = True, 1               # flat at this close (or closed at this open)
        else:
            state = 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
