"""Bollinger 20 x 2 re-entries with bar-count exits, six-day bars: the close crossing back above the lower band (or a
bar dipping below it and closing above) goes long; the mirror at the upper band goes short; from the 3rd bar of a
trade a close below the lower third closes the long, from the 10th bar a close below the basis does (shorts
mirrored); the source's band-distance trail is pending.
Port of FMZ strategy #489010 "多层级布林带趋势跟踪与反转交易策略-Multi-level-Bollinger-Bands-Trend-Following-and-Reversal-Trading-Strategy" (Bollinger Bands Strategy).

FMZ source id: 489010

Source
    https://www.fmz.com/strategy/489010 (PineScript v6, FMZ last modified 2025-04-01 10:16:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 157-249), BB 20 x 2, X 3, Y 10, trail retreat Z 30 %
    long = crossover(close, lower) or (low < lower and close > lower);  short = crossunder(close, upper) or (high > upper and close < upper)
    bars since entry counted while held (reset only when flat)
    long held: bars >= 3 and close < lower + (basis - lower) / 3 -> close; bars >= 10 and close < basis -> close
    long held: exit(trail_price = entry + 2 x (entry - lower), trail_offset = (entry - lower) x 0.7) every bar; shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar-count exits are close-checked signals (rule 3); they act on the position held at the bar's start.
    * The trail: activation at entry + 2 x (entry - current lower band), offset 0.7 x that distance (trail_offset takes
      ticks; a price distance is passed, read as a price distance as #427592), re-issued every bar with the moving
      band: a per-trade, moving activation the house trail cannot express: mark trailing_stop_pending, not emitted.
    * The counters and entry prices reset only on a flat bar, as written (a direct reversal keeps the old count).
      Entries reverse (REVERSAL INTENDED); on a bar with both signals the short (written last) wins.
    * FREQ = "6D" from the backtest header (period 6d): six-day bars from broker days in fixed blocks of six
      broker-day dates counted from 1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked exits; the trail pending (mark).
    2 generic: PASS, band positions and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the trail quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489010_bb_reentry_bar_count_exits_6d"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "6D"  # backtest header period: 6d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "x_bars": [3, 2],
    "y_bars": [10, 5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "x_bars": 3, "y_bars": 10}


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


def _multiday(raw_1m_df, days=6):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=6)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    le = (((c > lower) & (c.shift(1) <= lower.shift(1))) | ((lo < lower) & (c > lower))).to_numpy()
    se = (((c < upper) & (c.shift(1) >= upper.shift(1))) | ((h > upper) & (c < upper))).to_numpy()
    cv, bv, uv, lv = c.to_numpy(dtype=float), basis.to_numpy(), upper.to_numpy(), lower.to_numpy()
    X, Y = int(p["x_bars"]), int(p["y_bars"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held = pos = 0
    lb = sb = 0
    for i in range(m):
        start = held
        pos = held
        if le[i]:
            pos = 1
        if se[i]:
            pos = -1
        if held > 0:
            lb += 1
            lvl1 = lv[i] + (bv[i] - lv[i]) / 3
            if ((lb >= X and cv[i] < lvl1) or (lb >= Y and cv[i] < bv[i])) and start == 1 and pos == 1:
                pos = 0
        if held < 0:
            sb += 1
            lvl1 = uv[i] - (uv[i] - bv[i]) / 3
            if ((sb >= X and cv[i] > lvl1) or (sb >= Y and cv[i] > bv[i])) and start == -1 and pos == -1:
                pos = 0
        if held == 0:
            lb = sb = 0
        tgt[i] = pos
        held = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
