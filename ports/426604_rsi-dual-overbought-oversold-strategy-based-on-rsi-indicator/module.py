"""RSI(5) 80 / 20 contrarian with a 1.3 % target: RSI crossing above 80 goes short, crossing under
20 goes long; every position takes profit 1.3 % away.
Port of FMZ strategy #426604 "RSI Dual Overbought Oversold Strategy Based on RSI Indicator".

Source
    https://www.fmz.com/strategy/426604 (PineScript v4, FMZ last modified 2023-09-13 16:58:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 84-107), RSI 5, 80 / 20
    crossover(rsi(close, 5), 80)  -> entry short
    crossunder(rsi(close, 5), 20) -> entry long
    strategy.exit(profit = close * 0.013 / mintick)   (all entries, re-issued every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target distance is 1.3 % of the close of the bar that re-issues the exit, so the level
      moves after entry: rule 2, mark trailing_stop_pending. The port fixes it at 1.3 % of the
      fill price (tp_stop 0.013).
    * The stochastic RSI only plots. Entries do not depend on the position (a same-side signal
      while held is ignored by Pine and the engine alike), so nothing needs mirroring.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4D" from the backtest header (period 4d). Four-day bars are built from broker days
      (session ending 17:00 New York), in fixed blocks of four broker-day dates counted from
      1970-01-01 (block phase: decision owed), stamped with the first session start. Target on
      4-day bars: coarse_bar_stop.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426604_rsi5_contrarian_target"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [5, 7],
    "upper": [70, 80],
    "tp_pct": [1.3, 3.0],
}
DEFAULT_PARAMS = {"rsi_len": 5, "upper": 80, "tp_pct": 1.3}  # lower = 100 - upper


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


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
        key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=4)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi_pine(bars_df["close"], int(p["rsi_len"]))
    r1 = rsi.shift(1)
    up, lo = p["upper"], 100 - p["upper"]
    se = (rsi > up) & (r1 <= up)
    le = (rsi < lo) & (r1 >= lo)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
