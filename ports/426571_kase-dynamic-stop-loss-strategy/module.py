"""Kase dev stops (HPotter, always in): long while the close is at or above the level-4 Kase
deviation stop, short while it is below. The stop sits under the 20-bar high band when the
random-walk peak index Pk is positive, above the 20-bar low band otherwise.
Port of FMZ strategy #426571 "Kase Dynamic Stop Loss Strategy".

Source
    https://www.fmz.com/strategy/426571 (PineScript v2/v3 syntax, FMZ last modified 2023-09-13 14:08:47).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 121-145), Length 30, Level 4
    RWH = (high - low[30]) / (atr(30) sqrt(30)); RWL = (high[30] - low) / (atr(30) sqrt(30))
    Pk = wma(RWH - RWL, 3)
    r = highest(high, 2) - lowest(low, 2); AVTR = sma(r, 20); SD = stdev(r, 20)
    Val4 = Pk > 0 ? highest(high - AVTR - 3 SD, 20) : lowest(low + AVTR + 3 SD, 20)
    close < Val4 -> entry short, else -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * While Val4 is na (warm-up) close < na is false, so the source is long, as in Pine.
    * stdev is Pine's population deviation. "Trade reverse" off (source default).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426571_kase_dev_stop"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30, 50],
    "level": [2, 3, 4],
}
DEFAULT_PARAMS = {"length": 30, "level": 4}


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
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    scale = _atr_pine(bars_df, n) * np.sqrt(n)
    pk = _wma((h - l.shift(n)) / scale - (h.shift(n) - l) / scale, 3)
    r = h.rolling(2).max() - l.rolling(2).min()
    avtr, sd = r.rolling(20).mean(), r.rolling(20).std(ddof=0)
    k = float(p["level"]) - 1  # SD multiple: level 4 -> 3, ..., level 1 -> 0
    up = (h - avtr - k * sd).rolling(20).max()
    dn = (l + avtr + k * sd).rolling(20).min()
    res = up.where(pk > 0, dn)
    short = (c < res).to_numpy()
    return _always_in(~short, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
