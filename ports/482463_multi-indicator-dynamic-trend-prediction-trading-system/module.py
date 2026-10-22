"""RSI 14 and Stochastic 14 extremes with daily pivot filters, hourly bars: RSI under 30 with %K under 20 and the close above the last confirmed daily pivot low (0 when none) goes long; RSI over 70 with %K over 80 and the close under the daily pivot high goes short (only when one was confirmed); RSI or %K back over / under 50 closes.
Port of FMZ strategy #482463 "Multi Indicator Dynamic Trend Prediction Trading System" (Intraday Leading Indicator Strategy).

FMZ source id: 482463

Source
    https://www.fmz.com/strategy/482463 (PineScript v5, FMZ last modified 2025-02-18 15:22:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-151), RSI 14, 70 / 30; Stoch 14, 80 / 20; pivots request.security("D", pivothigh(high, 3, 3) / pivotlow(low, 3, 3))
    rsi < 30 and k < 20 and close > nz(pivotLow) -> entry Long;  rsi > 70 and k > 80 and close < nz(pivotHigh) -> entry Short
    rsi > 50 or k > 50 -> close Long;  rsi < 50 or k < 50 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily pivots come from a higher time frame without lookahead: each hourly bar uses the value of
      the last completed broker day, and that value is na except on the day a pivot is confirmed (3 days
      after it), as written: nz gives 0, so the long filter passes on every other day and the short needs
      a pivot confirmed the day before. The pivots are strict on both sides (as #478737). %K is na when the
      range is 0. The entries come before the closes: an entry that reverses a position stands although
      the other side's close is true on that bar (as #441963). REVERSAL INTENDED. No sizing code. Daily
      values are on broker days (17:00 America/New_York). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous broker day's pivots.
    2 generic: PASS, RSI / Stochastic extremes with daily pivot filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily pivots.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482463_rsi_stoch_extreme_prev_day_pivot_filter_mid_exit_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "stoch_k": [14, 21],
}
DEFAULT_PARAMS = {"rsi_length": 14, "stoch_k": 14, "rsi_overbought": 70, "rsi_oversold": 30,
                  "stoch_overbought": 80, "stoch_oversold": 20, "pivot_span": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["stoch_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100 * (c - ll) / (hh - ll).replace(0.0, np.nan)
    day = broker_day(c.index)
    dh, dl = h.groupby(day).max(), lo.groupby(day).min()
    sp = int(p["pivot_span"])
    ph = dh.shift(sp).where(pd.Series(_pivot(dh, 1, sp), index=dh.index))
    pl = dl.shift(sp).where(pd.Series(_pivot(dl, -1, sp), index=dl.index))
    ph0 = pd.Series(ph.shift(1).reindex(day).to_numpy(), index=c.index)    # last completed day
    pl0 = pd.Series(pl.shift(1).reindex(day).to_numpy(), index=c.index)
    le = (r < float(p["rsi_oversold"])) & (k < float(p["stoch_oversold"])) & (c > pl0.fillna(0.0))
    se = (r > float(p["rsi_overbought"])) & (k > float(p["stoch_overbought"])) & (c < ph0.fillna(0.0))
    lx = (r > 50) | (k > 50)
    sx = (r < 50) | (k < 50)
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def portfolio_kwargs(**params):
    return {}
