"""Five-bar swing reversal patterns with a 1.5 ATR stop and a 3 ATR target, two-day bars: when the previous bar's low is
below the four around it (a "double bottom" as written) and the current bar is green the strategy goes long; the
mirror with highs and a red bar goes short.
Port of FMZ strategy #484101 "多维图表模式量化策略融合头肩顶底与双顶底形态的技术分析交易系统-Multi-Dimensional-Chart-Pattern-Quantitative-Strategy-A-Technical-Analysis-Trading-System-Integrating-Head-and-Shoulders-and-Double-Top-Bottom-Formations" (Chart Pattern Strategy - Head and Shoulders / Double Top/Bottom).

FMZ source id: 484101

Source
    https://www.fmz.com/strategy/484101 (PineScript v5, FMZ last modified 2025-02-28 10:19:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 203-245), ATR 14, stop 1.5 ATR, target 3 ATR
    doubleBottom = low[1] < low[2], low[0], low[3], low[4] and low[0] > low[2] and low[0] > low[3]
    long = doubleBottom and close > open -> entry + exit(stop = close - 1.5 ATR, limit = close + 3 ATR)
    short = doubleTop (highs mirrored) and close < open (mirrored bracket)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The patterns as written (the head-and-shoulders test equals the double-top test and is unused).
    * The bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop = 2 x that, shifted one bar
      inside stops() and re-based on the fill (house rule). A same-side signal while held re-places it: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of
      broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, bar patterns and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484101_five_bar_swing_pattern_bracket"
FAMILY = "chart_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.5],
    "atr_len": [14, 7],
}
DEFAULT_PARAMS = {"atr_len": 14, "sl_mult": 1.5, "tp_ratio": 2.0}


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
    return _multiday(raw_1m_df, days=2)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    h1, h2, h3, h4 = (h.shift(k) for k in (1, 2, 3, 4))
    l1, l2, l3, l4 = (lo.shift(k) for k in (1, 2, 3, 4))
    top = (h1 > h2) & (h1 > h) & (h1 > h3) & (h1 > h4) & (h < h2) & (h < h3)
    bot = (l1 < l2) & (l1 < lo) & (l1 < l3) & (l1 < l4) & (lo > l2) & (lo > l3)
    long_e = (bot & (c > o)).astype(bool)
    short_e = (top & (c < o)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
