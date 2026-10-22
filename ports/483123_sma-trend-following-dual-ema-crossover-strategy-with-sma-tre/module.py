"""EMA 9 / 21 crossings on the SMA 15 side with candle colour filters, 4-day bars: an up-cross on two green candles with both EMAs and the close over the SMA goes long with the signal bar's low as stop and a 4R target, the mirror on a red candle goes short; reversing.
Port of FMZ strategy #483123 "趋势跟踪型双均线交叉策略结合SMA趋势过滤系统-Trend-Following-Dual-EMA-Crossover-Strategy-with-SMA-Trend-Filtering-System" (EMA Crossover Strategy with 15 SMA Trend).

FMZ source id: 483123

Source
    https://www.fmz.com/strategy/483123 (PineScript v5, FMZ last modified 2025-02-21 14:35:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-151), SMA 15; EMA 9 / 21; stop at the signal bar's low / high; target 4R; margin 100 / 100
    crossover(ema9, ema21) and close > sma15 and two green candles and ema9 > sma15 and ema21 > sma15 -> entry Long + exit(stop = low, limit = close + 4 (close - low))
    crossunder(ema9, ema21) and close < sma15 and red candle and both EMAs < sma15 -> entry Short + exit(stop = high, limit = close - 4 (high - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal bar and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). The crossings alternate. An entry on
      the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on
      bars longer than 1 hour: mark coarse_bar_stop. No sizing code (margin 100 / 100). Bars are blocks of
      four broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute.
      FREQ = "4D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an SMA side and candle filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: four-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483123_ema9_21_cross_sma15_side_candles_bar_stop_4r_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4D"  # backtest header period: 4d (four broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma_length": [15, 30],
    "rr": [4.0, 2.0],
}
DEFAULT_PARAMS = {"sma_length": 15, "rr": 4.0, "days": 4}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    sma = c.rolling(int(p["sma_length"])).mean()
    e9, e21 = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    xu = (e9 > e21) & (e9.shift(1) <= e21.shift(1))
    xd = (e9 < e21) & (e9.shift(1) >= e21.shift(1))
    two_green = (c > o) & (c.shift(1) > o.shift(1))
    le = xu & (c > sma) & two_green & (e9 > sma) & (e21 > sma)
    se = xd & (c < sma) & (c < o) & (e9 < sma) & (e21 < sma)
    rr = float(p["rr"])
    lvl = {"l_sl": lo, "l_tp": c + rr * (c - lo), "s_sl": h, "s_tp": c - rr * (h - c)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
