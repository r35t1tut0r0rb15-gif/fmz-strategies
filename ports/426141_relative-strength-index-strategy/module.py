"""QuantNomad RSI: RSI 3 crossing above 47 goes long, crossing below 56 goes short (always in).
Port of FMZ strategy #426141 "QuantNomad - RSI Strategy - LTCUSDT - 5m".

Source
    https://www.fmz.com/strategy/426141 (PineScript v4, FMZ last modified 2023-09-08 16:10:13).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 55-77), RSI 3, 47 / 56
    crossover(rsi, 47) -> entry long;  crossunder(rsi, 56) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The title says 5m, but the backtest header runs daily bars: FREQ from the header.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426141_rsi3_47_56_flip"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 5, 7],
    "over_sold": [40, 47],
    "over_bought": [56, 60],
}
DEFAULT_PARAMS = {"length": 3, "over_sold": 47, "over_bought": 56}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


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
    r = _rsi(bars_df["close"], int(p["length"]))
    os_, ob = p["over_sold"], p["over_bought"]
    up = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    dn = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
