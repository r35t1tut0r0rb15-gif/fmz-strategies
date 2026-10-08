"""Range MACD / RSI on opens (always in): the MACD histogram of the open crossing above 0 with
RSI(14) of the open at or under 55 goes long; crossing below 0 with RSI at or over 50 goes short.
Port of FMZ strategy #426588 "MACD RSI Trading Strategy for Oscillating Markets".

Source
    https://www.fmz.com/strategy/426588 (PineScript v5, FMZ last modified 2023-09-13 15:14:43).
    Verbatim copy: original_source.md. Read 2026-10-08 (re-read; rejected in batch A23 for
    pyramiding 2 stacking, which SURVEY_README classes as sizing).

Original signal (original_source.md lines 105-128), RSI 14 55 / 50, MACD 12 / 26 / 9 on open
    vrsi = rsi(open, 14); delta = macd(open) - ema(macd, 9)
    crossover(delta, 0) and vrsi <= 55 -> entry long;  crossunder(delta, 0) and vrsi >= 50 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 2: a second same-side entry is an add (sizing); the net position is ported.
    * The date window (from 2022-06-13) is a backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426588_open_macd_rsi_range"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "over_sold": [55, 45],
    "over_bought": [50, 60],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 55, "over_bought": 50, "fast": 12, "slow": 26, "signal": 9}


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


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
    o = bars_df["open"]
    rsi = _rsi_pine(o, int(p["length"]))
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    macd = ema(o, p["fast"]) - ema(o, p["slow"])
    d = macd - ema(macd, p["signal"])
    d1 = d.shift(1)
    ok = rsi.notna()
    long_ = (ok & (d > 0) & (d1 <= 0) & (rsi <= p["over_sold"])).to_numpy()
    short = (ok & (d < 0) & (d1 >= 0) & (rsi >= p["over_bought"])).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
