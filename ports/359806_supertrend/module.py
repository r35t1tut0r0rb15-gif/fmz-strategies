"""SuperTrend side with a band-slope filter: long in an up-trend whose line rose over 2 bars,
short in a down-trend whose line fell over 3 bars; otherwise only close the opposite side.
Port of FMZ strategy #359806 "超级趋势策略SuperTrend".

Source
    https://www.fmz.com/strategy/359806 (PineScript, FMZ last modified 2024-08-30 18:24:36).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 66-82), factor 5, atrPeriod 10
    [supertrend, direction] = ta.supertrend(5, 10)
    direction < 0:  supertrend > supertrend[2] -> entry long;  else if short -> close_all
    direction > 0:  supertrend < supertrend[3] -> entry short; else if long  -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as in Pine v5 (hl2 bands, Wilder ATR, ratcheting, direction flip rule).
    * strategy.entry reverses an opposite position: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies). close_all -> exit signals.
    * Daily bars (backtest period 1d) are broker days (17:00 New York).
    * The 50 % of equity order size is sizing (original_sizing.txt).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_359806_supertrend_slope_filter"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 5.0, 7.0],
    "atr_period": [7, 10, 14],
}
DEFAULT_PARAMS = {"factor": 5.0, "atr_period": 10}


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


def _supertrend(bars, factor, atr_period):
    """ta.supertrend(factor, atrPeriod) as in Pine v5: returns (supertrend, direction);
    direction < 0 is an up-trend."""
    atr = _atr_pine(bars, atr_period).to_numpy()
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hl2 = (h + lo) / 2
    m = len(c)
    st, dirn = np.full(m, np.nan), np.full(m, np.nan)
    lower_prev = upper_prev = 0.0      # nz(...[1])
    st_prev = np.nan
    for i in range(m):
        lower, upper = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        if i > 0:
            if not (lower > lower_prev or c[i - 1] < lower_prev):
                lower = lower_prev
            if not (upper < upper_prev or c[i - 1] > upper_prev):
                upper = upper_prev
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_prev == upper_prev:
            d = -1 if c[i] > upper else 1
        else:
            d = 1 if c[i] < lower else -1
        st[i] = lower if d == -1 else upper
        dirn[i] = d
        lower_prev = 0.0 if np.isnan(lower) else lower
        upper_prev = 0.0 if np.isnan(upper) else upper
        st_prev = st[i]
    return pd.Series(st, index=bars.index), pd.Series(dirn, index=bars.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    st_s, dir_s = _supertrend(bars_df, p["factor"], int(p["atr_period"]))
    st, dirn = st_s.to_numpy(), dir_s.to_numpy()
    st2, st3 = st_s.shift(2).to_numpy(), st_s.shift(3).to_numpy()

    m = len(st)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if dirn[i] < 0:
            if st[i] > st2[i]:
                if pos != 1:
                    le[i], pos = True, 1
            elif pos < 0:
                sx[i], pos = True, 0
        elif dirn[i] > 0:
            if st[i] < st3[i]:
                if pos != -1:
                    se[i], pos = True, -1
            elif pos > 0:
                lx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
