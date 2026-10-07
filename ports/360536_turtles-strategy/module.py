"""Turtle system (Pine): 20-bar breakout after a losing trade or 55-bar fail-safe breakout,
10-bar opposite-channel exit, 2N stop from the last unit.
Port of FMZ strategy #360536 "海龟交易法Turtles-strategy".

Source
    https://www.fmz.com/strategy/360536 (PineScript, FMZ last modified 2022-05-21 20:43:32).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 41-140), ATR 20, BO 20, FS 55, TE 10
    N = ta.atr(20); donchianHi = ta.highest(high[1], 20) ... (prior bars)
    flat and (PreBreakoutFailure or filter off): high > donchianHi -> long; low < donchianLow -> short
    flat: high > fsDonchianHi -> long;  low < fsDonchianLo -> short     (PreEntryPrice := high/low)
    long:  low < lowest(low[1], 10) -> close_all
           else: high >= PreEntryPrice + 0.5N -> add (PreEntryPrice := high)
                 low <= PreEntryPrice - 2N and no order this bar -> close_all, PreBreakoutFailure := true
    short: mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * All rules are evaluated at the bar close on the bar's high/low and send market orders, so
      they are signals on the completed bar, filled at the next open (no intrabar stop).
    * Pyramid adds (pyramiding = 4, unit size from equity/N) are sizing (original_sizing.txt),
      but they move PreEntryPrice, which the 2N stop uses, so the add rule is kept as state.
    * If several entry lines fire on one flat bar, the last one in source order decides the
      direction (Pine fills the pending entries in order at the next open).
    * Entries only from flat: opposite entries cannot occur; portfolio_kwargs also returns
      upon_opposite_entry="ignore" (rule 6).
    * Daily bars (backtest period 1d) are broker days (17:00 New York).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_360536_turtle_20_55_pine"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bo_length": [10, 20, 30],
    "fs_length": [40, 55, 80],
    "te_length": [5, 10, 15],
}
DEFAULT_PARAMS = {"bo_length": 20, "fs_length": 55, "te_length": 10, "atr_length": 20,
                  "stop_n": 2.0, "add_n": 0.5, "profitable_filter": True}


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


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hs, ls = bars_df["high"].shift(1), bars_df["low"].shift(1)
    bo_hi = hs.rolling(int(p["bo_length"])).max().to_numpy()
    bo_lo = ls.rolling(int(p["bo_length"])).min().to_numpy()
    fs_hi = hs.rolling(int(p["fs_length"])).max().to_numpy()
    fs_lo = ls.rolling(int(p["fs_length"])).min().to_numpy()
    te_hi = hs.rolling(int(p["te_length"])).max().to_numpy()
    te_lo = ls.rolling(int(p["te_length"])).min().to_numpy()
    n = _atr_pine(bars_df, int(p["atr_length"])).to_numpy()
    h, lo = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)

    m = len(h)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, failure = 0, np.nan, False
    for i in range(m):
        if np.isnan(n[i]):
            continue
        if pos == 0:
            fired = []
            if (not p["profitable_filter"]) or failure:
                if h[i] > bo_hi[i]:
                    fired.append((1, h[i]))
                if lo[i] < bo_lo[i]:
                    fired.append((-1, lo[i]))
            if h[i] > fs_hi[i]:
                fired.append((1, h[i]))
            if lo[i] < fs_lo[i]:
                fired.append((-1, lo[i]))
            if fired:
                pos, ref = fired[-1]
                failure = False
                (le if pos == 1 else se)[i] = True
            continue
        if pos == 1:
            if lo[i] < te_lo[i]:
                lx[i], pos = True, 0
                continue
            sent = False
            if h[i] >= ref + p["add_n"] * n[i]:
                ref, sent = h[i], True
            if lo[i] <= ref - p["stop_n"] * n[i] and not sent:
                lx[i], pos, failure = True, 0, True
        else:
            if h[i] > te_hi[i]:
                sx[i], pos = True, 0
                continue
            sent = False
            if lo[i] <= ref - p["add_n"] * n[i]:
                ref, sent = lo[i], True
            if h[i] >= ref + p["stop_n"] * n[i] and not sent:
                sx[i], pos, failure = True, 0, True

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
