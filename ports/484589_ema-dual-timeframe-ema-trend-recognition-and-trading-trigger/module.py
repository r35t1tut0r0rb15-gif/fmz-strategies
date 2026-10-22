"""Hourly EMA 12 / 26 crossings or 5 % candles in the direction of the daily EMA 5 / 30 trend (last completed broker day), hourly bars: a bullish trigger in a daily uptrend goes long with the 10-bar low as stop, a bearish trigger in a downtrend goes short with the 10-bar high as stop; reversing.
Port of FMZ strategy #484589 "双时间框架EMA趋势识别与交易触发量化策略-Dual-Timeframe-EMA-Trend-Recognition-and-Trading-Trigger-Quantitative-Strategy" (EMA Trend & Trigger Strategy).

FMZ source id: 484589

Source
    https://www.fmz.com/strategy/484589 (PineScript v5, FMZ last modified 2025-03-03 10:28:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 248-297), daily EMA 5 / 30 via security("1D"); hourly EMA 12 / 26 via security("60"); 5 % candle trigger; stop at the 10-bar low / high
    uptrend = security("1D", ema5) > security("1D", ema30);  buy = crossover(ema12, ema26) and uptrend;  highVolUp = (close - open) / open > 5 % and uptrend
    buy or highVolUp -> entry Long + exit(stop = lowest(low, 10));  sell or highVolDown -> entry Short + exit(stop = highest(high, 10))

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("1D") without lookahead on the hourly chart is read as the EMAs of the last broker day
      completed by the bar's close (a day completes at 17:00 New York), built in precompute from the
      minutes (as #440503); security("60") on the hourly chart is the chart's own EMAs.
    * The stop is fixed at the signal bar's 10-bar extreme and sent as a fraction of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256). A repeat trigger while
      held re-sends the stop from the new extreme; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL INTENDED); a short
      called on the same bar as a long wins (called later, as #437773). Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing stop as a fraction of the fill.
    2 generic: PASS, hourly EMA crossings in the daily EMA trend.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily EMAs.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484589_daily_ema5_30_trend_hourly_ema12_26_cross_swing_stop_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_ema_1d": [5, 10],
    "short_ema_1h": [12, 9],
}
DEFAULT_PARAMS = {"short_ema_1d": 5, "short_ema_1h": 12, "long_ema_1d": 30, "long_ema_1h": 26, "swing": 10,
                  "candle_pct": 5.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    cl = raw_1m_df["close"].dropna()
    dclose = cl.groupby(broker_day(cl.index)).last()
    es = dclose.ewm(span=int(p["short_ema_1d"]), adjust=False).mean().to_numpy()
    el = dclose.ewm(span=int(p["long_ema_1d"]), adjust=False).mean().to_numpy()
    day_end = (pd.DatetimeIndex(dclose.index) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bar_end = bars.index + pd.Timedelta(hours=1)
    pos = np.searchsorted(day_end.tz_convert("UTC").asi8, bar_end.tz_convert("UTC").asi8, side="right") - 1
    ok = pos >= 0
    bars["d_short"] = np.where(ok, es[np.clip(pos, 0, None)], np.nan)
    bars["d_long"] = np.where(ok, el[np.clip(pos, 0, None)], np.nan)
    return bars


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    up = bars_df["d_short"] > bars_df["d_long"]
    dn = bars_df["d_short"] < bars_df["d_long"]
    f = c.ewm(span=int(p["short_ema_1h"]), adjust=False).mean()
    s = c.ewm(span=int(p["long_ema_1h"]), adjust=False).mean()
    chg = (c - o) / o * 100
    k = float(p["candle_pct"])
    le = (((f > s) & (f.shift(1) <= s.shift(1))) | (chg > k)) & up
    se = (((f < s) & (f.shift(1) >= s.shift(1))) | (chg < -k)) & dn
    n = int(p["swing"])
    return le & ~se, se, {"l_sl": lo.rolling(n).min(), "s_sl": h.rolling(n).max()}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    lx = lf & (lvl["l_sl"].shift(1) >= o)      # marketable at the fill: closed one bar late
    sx = sf & (lvl["s_sl"].shift(1) <= o)
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    return {"sl_stop": sl.where(sl > 0)}


def portfolio_kwargs(**params):
    return {}
