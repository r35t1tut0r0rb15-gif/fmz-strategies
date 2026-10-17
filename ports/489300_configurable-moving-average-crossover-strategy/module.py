"""Configurable MA 13 / 55 / 34 trend entries with an exit-MA close after two bars, long by default, two-day bars: the
close crossing above MA 13 with MA 13 above MA 55 and the close above MA 34 goes long; from the second bar of the
trade a close below MA 34 closes it; with shorts on, the mirror.
Port of FMZ strategy #489300 "可配置移动平均线交叉策略-Configurable-Moving-Average-Crossover-Strategy" (Configurable MA Cross (MA-X) Strategy).

FMZ source id: 489300

Source
    https://www.fmz.com/strategy/489300 (PineScript v6, FMZ last modified 2025-04-03 11:31:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 130-196), MA 13 / 55 / 34, EMA, shorts off
    goLong = close > maA and maA > maB and close > maC and crossover(close, maA)   (goShort mirrored, if enabled)
    barSinceEntry: na when no trade is open, else counts up; set to 1 on every entry signal
    exitLong = long and barSinceEntry >= 2 and close < maC -> close;  exitShort mirrored
    goLong -> close "Short", entry long;  goShort -> close "Long", entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * barSinceEntry is the source's counter: it counts bars while a trade is open (the fill bar is 1) and is reset to
      1 by any entry signal, also one that is ignored because the trade is already open.
    * Shorts are off by default; the switch is a declared GRID variant. With shorts on, entries reverse (REVERSAL
      INTENDED, closes before entries); long only by default.
    * MA types SMA / EMA / WMA / HMA as the source's input (EMA default; the grid also tries SMA). The commission is a
      cost (not in the module).
    * FREQ = "2D" from the backtest header (period 2d): two-day bars from broker days in fixed blocks counted from
      1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED (with shorts on); long only by default.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489300_configurable_ma_cross_exit_ma"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": ["EMA", "SMA"],
    "enable_shorts": [False, True],
}
DEFAULT_PARAMS = {"ma_a": 13, "ma_b": 55, "ma_c": 34, "ma_type": "EMA", "enable_shorts": False}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _ma(x, n, kind):
    if kind == "SMA":
        return x.rolling(n).mean()
    if kind == "EMA":
        return x.ewm(span=n, adjust=False).mean()
    if kind == "WMA":
        return _wma(x, n)
    return _wma(2 * _wma(x, max(int(n / 2), 1)) - _wma(x, n), max(int(round(np.sqrt(n))), 1))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b, cc = (_ma(c, int(p[k]), p["ma_type"]) for k in ("ma_a", "ma_b", "ma_c"))
    go_long = ((c > a) & (a > b) & (c > cc) & (c > a) & (c.shift(1) <= a.shift(1))).to_numpy()
    go_short = ((c < a) & (a < b) & (c < cc) & (c < a) & (c.shift(1) >= a.shift(1))).to_numpy()
    if not p["enable_shorts"]:
        go_short = np.zeros(len(c), dtype=bool)
    below, above = (c < cc).to_numpy(), (c > cc).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0          # target after this bar's orders
    held = 0         # position during this bar (filled at its open)
    bse = None
    for i in range(m):
        bse = None if held == 0 else (1 if bse is None else bse + 1)
        start = pos
        if go_long[i]:
            pos, bse = 1, 1
        if go_short[i]:
            pos, bse = -1, 1
        if held == 1 and start == 1 and pos == 1 and bse is not None and bse >= 2 and below[i]:
            pos = 0
        if held == -1 and start == -1 and pos == -1 and bse is not None and bse >= 2 and above[i]:
            pos = 0
        tgt[i] = pos
        held = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
