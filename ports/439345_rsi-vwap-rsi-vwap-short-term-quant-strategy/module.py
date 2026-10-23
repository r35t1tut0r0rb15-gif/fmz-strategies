"""Hourly bars, long only: the RSI 17 of the session VWAP crossing over 19 goes long; crossing under 80 closes it.
Port of FMZ strategy #439345 "基于RSI和VWAP的短线量化策略RSI-VWAP-Short-term-Quant-Strategy" (RSI-VWAP INDICATOR (Xaviz)).

FMZ source id: 439345

Source
    https://www.fmz.com/strategy/439345 (PineScript v4, FMZ last modified 2024-01-19 14:21:15).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 148-173), RSI-VWAP length 17; oversold 19; overbought 80
    RSI_VWAP = rsi(vwap(close), 17)
    crossover(RSI_VWAP, 19) -> entry Long;  crossunder(RSI_VWAP, 80) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * vwap(close) is the session VWAP, anchored at the broker-day start (as earlier ports); the RSI is
      Pine's (rma). Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI of the session VWAP leaving oversold / overbought.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439345_rsi17_of_session_vwap_19_80_1h_long_only"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [17, 14],
    "over_sold": [19.0, 30.0],
}
DEFAULT_PARAMS = {"length": 17, "over_sold": 19.0, "over_bought": 80.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    r = _rsi(vwap, int(p["length"]))
    os_, ob = float(p["over_sold"]), float(p["over_bought"])
    buy = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    sell = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
