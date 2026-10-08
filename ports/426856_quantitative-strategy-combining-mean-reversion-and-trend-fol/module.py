"""Mean reversion + trend following, long only: from flat, above SMA 200 go long (trend trade);
below it, RSI(2) under 20 goes long (mean-reversion trade). A trend trade is closed when the
close falls 5 % under SMA 200, a mean-reversion trade when RSI(2) rises over 80.
Port of FMZ strategy #426856 "Quantitative Strategy Combining Mean Reversion and Trend Following".

Source
    https://www.fmz.com/strategy/426856 (PineScript v5, FMZ last modified 2023-09-14 20:45:20).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 142-179), SMA 200, RSI 2, both modes on
    isBuy = (close < sma200 and rsi2 < 20) or (close > sma200)
    isBuy and no open trade -> entry long; origin = close > sma200 ? "SMA" : "RSI"
    isClose = origin == "SMA" ? close < 0.95 sma200 : rsi2 > 80
    isClose -> strategy.exit(limit = close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is a limit order at the bar's close, re-issued while the condition holds. Ported
      as a close-based exit signal filled at the next open (decision owed: Pine fills it at
      max(open, limit) once the high reaches the limit).
    * The origin is set on the signal bar and kept until the next entry. The position factor
      (1 / 0.5 of equity) is sizing.
    * Long only. Daily bars are broker days (session ending 17:00 New York), stamped with the
      session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426856_mean_reversion_trend_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [100, 200],
    "rsi_buy": [10, 20],
    "rsi_close": [70, 80],
}
DEFAULT_PARAMS = {"sma_len": 200, "rsi_len": 2, "rsi_buy": 20, "rsi_close": 80, "sma_close": 0.95}


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


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    rsi = _rsi_pine(c, int(p["rsi_len"]))
    sma_buy = (c > sma).to_numpy()
    rsi_buy = ((c < sma) & (rsi < p["rsi_buy"])).to_numpy()
    sma_close = (c < sma * p["sma_close"]).to_numpy()
    rsi_close = (rsi > p["rsi_close"]).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos, origin = 0, ""
    for i in range(len(c)):
        if pos == 0 and (sma_buy[i] or rsi_buy[i]):
            pos, origin = 1, ("SMA" if sma_buy[i] else "RSI")
        elif pos == 1 and (sma_close[i] if origin == "SMA" else rsi_close[i]):
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
