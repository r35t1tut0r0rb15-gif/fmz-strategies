"""RSI 14 above its last trough (long) or below its last peak (short), with the stop at the previous bar's low (high)
and a 4 R target, two-day bars.
Port of FMZ strategy #482644 "动态RSI突破趋势跟踪交易策略结合风险收益比优化系统-Dynamic-RSI-Breakout-Trend-Following-Trading-Strategy-with-Risk-Reward-Ratio-Optimization-System" (RSI Breakout Strategy with RR 1:4).

FMZ source id: 482644

Source
    https://www.fmz.com/strategy/482644 (PineScript v6, FMZ last modified 2025-02-19 14:59:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-143), RSI 14, RR 4
    rsi turning up (rsi > rsi[1] < rsi[2]) -> rsi_prev_high := rsi[1]; turning down -> rsi_prev_low := rsi[1]
    rsi > rsi_prev_high -> entry long with exit(stop = low[1], limit = close + 4 (close - low[1]))
    rsi < rsi_prev_low -> entry short with exit(stop = high[1], limit = close - 4 (high[1] - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script carries //@version=6 and then //@version=5; the first (v6) is recorded. "rsi_prev_high" holds
      the last RSI trough (and "rsi_prev_low" the last peak), as written.
    * On a bar meeting both conditions the short entry, written later, wins (it reverses the long the earlier call
      opens).
    * The bracket is placed with the entry from the signal bar: (close - low[1]) / close and 4 x that for longs,
      mirrored for shorts, picked by the signal's side, shifted one bar inside stops() and re-based on the fill
      (house rule). A stop already beyond the close (zero-length trade) emits no entry (as L2 #491035). Each bar in
      the condition re-issues the exit while held: fixed at entry, mark trailing_stop_pending (as #491506).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of
      broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-issued bracket fixed at entry (marked).
    2 generic: PASS, RSI turning points and the previous bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482644_rsi_turn_level_break_prev_bar_stop_rr4_2d"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [14, 7],
    "rr": [4.0, 2.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rr": 4.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _hold(x):
    """A Pine var level: the last value set, kept until the next one (past values only)."""
    v = x.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=x.index)


def _parts(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    r1, r2 = r.shift(1), r.shift(2)
    trough = _hold(r1.where((r > r1) & (r1 < r2)))           # var: last value kept (past only)
    peak = _hold(r1.where((r < r1) & (r1 > r2)))
    sl_l, sl_s = (c - lo.shift(1)) / c, (h.shift(1) - c) / c
    long_c = (r > trough) & trough.notna() & (sl_l > 0)
    short_c = (r < peak) & peak.notna() & (sl_s > 0)
    long_e = long_c & ~short_c                                # the later short call wins
    return long_e.astype(bool), short_c.astype(bool), sl_l, sl_s


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _parts(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, sl_l, sl_s = _parts(bars_df, p)
    sl = sl_l.where(long_e, sl_s)                              # picked by the signal's side
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
