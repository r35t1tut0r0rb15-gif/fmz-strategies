"""Triple agreement on a new bar: EMA13/SMA23 cross, 50-bar return sign and the daily SuperTrend
direction; long on the first bar all three are bullish, short on the first bar all bearish.
Port of FMZ strategy #362499 "Moving-Average-Colored-EMA-SMA".

Source
    https://www.fmz.com/strategy/362499 (PineScript v5, FMZ last modified 2022-05-11 21:23:11).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-129), chart 1h
    bs1 = crossover(ema13, sma23) ? 1 : crossunder ? -1 : 0
    bs2 = (close - close[50]) / close[50] > 0 ? 1 : -1
    bs3 = daily ta.supertrend(3, 10) direction < 0 ? 1 : -1   (request.security 'D', lookahead_off)
    bs = all 1 -> 1, all -1 -> -1, else 0;  buy = bs == 1 and bs[1] != 1; sell mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily SuperTrend runs on broker days built from the hourly bars. Historical
      lookahead_off values are the last COMPLETED day's (the new day's value appears on the
      hourly bar that closes the day).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362499_ema_sma_cross_return_daily_st"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [9, 13, 21],
    "sma_len": [23, 50],
    "ret_len": [50, 100],
}
DEFAULT_PARAMS = {"ema_len": 13, "sma_len": 23, "ret_len": 50, "st_factor": 3.0, "st_atr": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
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


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    s = c.rolling(int(p["sma_len"])).mean()
    bs1 = np.where((e > s) & (e.shift(1) <= s.shift(1)), 1, np.where((e < s) & (e.shift(1) >= s.shift(1)), -1, 0))
    k = int(p["ret_len"])
    bs2 = np.where((c - c.shift(k)) / c.shift(k) > 0, 1, -1)
    day = broker_day(bars_df.index)
    daily = bars_df.groupby(day).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    d_dir = _supertrend(daily, p["st_factor"], int(p["st_atr"]))[1]
    end_ny = (bars_df.index + pd.Timedelta(hours=1)).tz_convert("America/New_York")
    at_close = np.asarray((end_ny.hour == 17) & (end_ny.minute == 0))
    today = d_dir.reindex(day).to_numpy()
    before = d_dir.shift(1).reindex(day).to_numpy()
    dd = np.where(at_close, today, before)
    bs3 = np.where(dd < 0, 1, -1)
    ready = ~np.isnan(dd) & c.shift(k).notna().to_numpy()
    bs = np.where(ready & (bs1 == 1) & (bs2 == 1) & (bs3 == 1), 1,
                  np.where(ready & (bs1 == -1) & (bs2 == -1) & (bs3 == -1), -1, 0))
    prev = np.roll(bs, 1)
    prev[0] = 0
    return _always_in((bs == 1) & (prev != 1), (bs == -1) & (prev != -1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
