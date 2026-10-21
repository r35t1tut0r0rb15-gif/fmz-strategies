"""Moving-average crossings with a choice of average type, broker days: the short average (SMA 5 by default) crossing over the long one (15) goes long, crossing under goes short; reversing.
Port of FMZ strategy #437376 "Nine Types of Moving Average Crossover Strategy" (kozlod_yamacs).

FMZ source id: 437376

Source
    https://www.fmz.com/strategy/437376 (PineScript v3, FMZ last modified 2024-01-02 10:37:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 168-287), MA type SMA (EMA, WMA, ALMA, VWMA, HMA, LSMA, SMMA, DEMA), short 5, long 15; SL / PT levels 0 (off)
    short_ma / long_ma = ma(close, 5 / 15) of the chosen type;  long_signal = crossover(short, long) -> entry long;  short_signal = crossunder -> entry short
    SL / PT: close-tested percent levels from the previous signal's next open, off by default (0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Eight average types are ported (SMA, EMA, WMA, ALMA, HMA with integer n / 2, LSMA = linreg value at
      offset 0, SMMA seeded with the SMA, DEMA); VWMA needs volume and is left out (check 8; not the
      default). The SL / PT levels are off by default (0) and not ported. REVERSAL INTENDED. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437376_ma_type_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": ["SMA", "EMA"],
    "short_len": [5, 10],
}
DEFAULT_PARAMS = {"ma_type": "SMA", "short_len": 5, "long_len": 15, "alma_offset": 0.85, "alma_sigma": 6.0,
                  "lsma_offset": 0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _alma(x, n, offset, sigma):
    m = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))     # oldest first, as Pine's loop
    w = w / w.sum()
    return x.rolling(n).apply(lambda v: np.dot(v, w), raw=True)


def _lsma(x, n, off):
    sx = n * (n - 1) / 2
    sxx = (n - 1) * n * (2 * n - 1) / 6
    sxy = sum((n - 1 - k) * x.shift(k) for k in range(n))
    sy = x.rolling(n).sum()
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1 - off)


def _smma(x, n):
    v = x.to_numpy(dtype=float)
    sma = x.rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        prev = out[i - 1] if i else np.nan
        out[i] = sma[i] if np.isnan(prev) else (prev * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _ma(x, n, kind, p):
    if kind == "SMA":
        return x.rolling(n).mean()
    if kind == "EMA":
        return x.ewm(span=n, adjust=False).mean()
    if kind == "WMA":
        return _wma(x, n)
    if kind == "ALMA":
        return _alma(x, n, float(p["alma_offset"]), float(p["alma_sigma"]))
    if kind == "HMA":
        return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))
    if kind == "LSMA":
        return _lsma(x, n, int(p["lsma_offset"]))
    if kind == "SMMA":
        return _smma(x, n)
    if kind == "DEMA":
        e1 = x.ewm(span=n, adjust=False).mean()
        return 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    raise ValueError(f"MA type {kind!r} not ported (VWMA needs volume, check 8)")


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = _ma(c, int(p["short_len"]), p["ma_type"], p)
    lg = _ma(c, int(p["long_len"]), p["ma_type"], p)
    up = (s > lg) & (s.shift(1) <= lg.shift(1))
    dn = (s < lg) & (s.shift(1) >= lg.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
