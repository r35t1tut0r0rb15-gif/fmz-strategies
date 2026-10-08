"""HKST cloud, long only: the high crossing above the top of a cloud spanned by a Kaufman AMA of
OHLC4, its Hull MA and a SuperTrend (2, 5) goes long; the low crossing under the cloud bottom,
or a close below it, closes the long.
Port of FMZ strategy #426619 "Trend Following Strategy Based on Triple Indicator Cloud Pattern".

Source
    https://www.fmz.com/strategy/426619 (PineScript v5, FMZ last modified 2023-09-13 17:38:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 95-137), Kaufman 20, Hull 20, SuperTrend 2 / 5
    x = ohlc4; er = sum(|x - x[1]|, 20) != 0 ? |x - x[20]| / sum(...) : 0
    sc = (er * (0.666 - 0.0645) + 0.0645)^2;  ama = nz(ama[1]) + sc * (x - nz(ama[1]))
    hull = hma(ama, 20);  [st, _] = supertrend(2, 5)
    band1 = max(st, hull, ama); band2 = min(st, hull, ama)
    crossover(high, band1) -> entry long;  crossunder(low, band2) or close < band2 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The AMA starts from 0 (nz) on the first bar, so its early values depend on where the data
      starts (decision owed, as #366388 / #370711): with a smoothing constant near 0.004 the
      start-up decays slowly.
    * While the noise sum is na, na != 0 is false and the efficiency ratio is 0, as in Pine.
    * strategy.close("Up", shortCondition): the second argument is `when` (Pine v5 of 2023).
    * Long only. Daily bars are broker days (session ending 17:00 New York), stamped with the
      session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426619_hkst_cloud_long"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kaufman_len": [10, 20],
    "hull_len": [20, 40],
    "atr_factor": [2.0, 3.0],
}
DEFAULT_PARAMS = {"kaufman_len": 20, "hull_len": 20, "atr_factor": 2.0, "atr_period": 5}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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


def _kama(x, n):
    noise = (x - x.shift(1)).abs().rolling(n).sum()
    signal = (x - x.shift(n)).abs()
    er = (signal / noise).where(noise.notna() & (noise != 0), 0.0)  # na != 0 is false -> 0
    sc = (er * (0.666 - 0.0645) + 0.0645) ** 2
    xv, sv = x.to_numpy(dtype=float), sc.to_numpy()
    out = np.zeros(len(xv))
    prev = 0.0
    for i in range(len(xv)):
        prev = prev + sv[i] * (xv[i] - prev)
        out[i] = prev
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    x = (bars_df["open"] + h + l + c) / 4
    ama = _kama(x, int(p["kaufman_len"]))
    n = int(p["hull_len"])
    hull = _wma(2 * _wma(ama, n // 2) - _wma(ama, n), int(round(np.sqrt(n))))
    st, _ = _supertrend(bars_df, p["atr_factor"], int(p["atr_period"]))
    three = pd.concat([st, hull, ama], axis=1)
    band1, band2 = three.max(axis=1, skipna=False), three.min(axis=1, skipna=False)
    le = (h > band1) & (h.shift(1) <= band1.shift(1))
    lx = ((l < band2) & (l.shift(1) >= band2.shift(1))) | (c < band2)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
