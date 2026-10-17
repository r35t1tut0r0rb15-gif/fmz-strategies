"""EMA 9 / 21 crosses with both EMAs and the close on the SMA 15 side and candle confirmation, stop at the signal
bar's extreme and a 4 R target, four-day bars: EMA 9 crossing above EMA 21 with the close, EMA 9 and EMA 21 above
SMA 15 and two green bars goes long (stop the signal bar's low, target close + 4 x (close - low)); the mirror with one
red bar goes short.
Port of FMZ strategy #483123 "趋势跟踪型双均线交叉策略结合SMA趋势过滤系统-Trend-Following-Dual-EMA-Crossover-Strategy-with-SMA-Trend-Filtering-System" (EMA Crossover Strategy with 15 SMA Trend).

FMZ source id: 483123

Source
    https://www.fmz.com/strategy/483123 (PineScript v5, FMZ last modified 2025-02-21 14:35:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-136), SMA 15, EMA 9 / 21, RR 4
    long = crossover(ema9, ema21) and close > sma15 and close > open and close[1] > open[1] and ema9 > sma15 and
    ema21 > sma15; entry + exit(stop = low, limit = close + 4 (close - low)) (short mirrored, one red bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: sl = (close - low) / close, tp = 4 x sl for a long
      ((high - close) / close for a short), picked by the signal's side, shifted one bar inside stops() and re-based on
      the fill (house rule). Both are positive under the candle conditions. A later same-side signal while held
      re-places it: mark trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
    * Four-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "4D" from the
      backtest header. Stops on four-day bars: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, candle colours and the signal bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in four-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483123_ema9_21_sma15_candle_bar_stop_4d"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [4.0, 2.0],
    "sma_len": [15, 30],
}
DEFAULT_PARAMS = {"sma_len": 15, "fast": 9, "slow": 21, "rr": 4.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=4)


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = c.rolling(int(p["sma_len"])).mean()
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    golden = (f > s) & (f.shift(1) <= s.shift(1))
    death = (f < s) & (f.shift(1) >= s.shift(1))
    two_bull = (c > o) & (c.shift(1) > o.shift(1))
    long_e = (golden & (c > sma) & two_bull & (f > sma) & (s > sma)).astype(bool)
    short_e = (death & (c < sma) & (c < o) & (f < sma) & (s < sma)).astype(bool)
    return long_e, short_e, (c - lo) / c, (h - c) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, d_long, d_short = _signals(bars_df, p)
    sl = d_long.where(long_e, d_short)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
