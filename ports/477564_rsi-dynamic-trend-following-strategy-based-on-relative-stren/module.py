"""RSI 14 over 60 with the close off its 55-bar low, broker days, long only: such a bar buys; a close at the 55-bar low with RSI under 60 closes; a 2 % stop from the entry price.
Port of FMZ strategy #477564 "基于相对强弱与RSI的动态趋势跟踪套利策略-Dynamic-Trend-Following-Strategy-Based-on-Relative-Strength-and-RSI" (Sanjay RS&RSI Strategy V3 for nifty 15min, SL-1.3).

FMZ source id: 477564

Source
    https://www.fmz.com/strategy/477564 (PineScript v5, FMZ last modified 2025-01-06 14:02:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-146), SuperTrend ATR 10 x 3 (outputs swapped); RS 55 (stochastic of closes); RSI 14, 60; stop 2 % of strategy.position_avg_price
    [stDir, st] = ta.supertrend(3, 10) (Pine returns [line, direction]);  stDir > 0 and rs > 0 and rsi > 60 -> entry Buy;  every bar: exit(Buy, stop = avg x 0.98)
    exit = (stDir < 0 and rs <= 0) or (stDir < 0 and rsi < 60) or (rs <= 0 and rsi < 60) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend returns [line, direction], so the script's "direction" is the SuperTrend LINE, a
      price that is always positive once it exists: the buy test reduces to rs > 0 and RSI over 60, and
      the exit to rs <= 0 (the close at its 55-bar low) with RSI under 60, as written. A zero 55-bar
      range gives na (no signal). The stop is sent from the position's average price: a scalar fraction of
      the entry fill, active from the fill (as #440797). Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price stop as a fraction of the fill.
    2 generic: PASS, RSI strength off the range low, as written (SuperTrend outputs swapped).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop percentage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_477564_rs55_off_low_rsi60_avg_stop_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rs_period": [55, 20],
    "rsi_threshold": [60.0, 50.0],
}
DEFAULT_PARAMS = {"rs_period": 55, "rsi_threshold": 60.0, "rsi_period": 14, "sl_pct": 0.02, "atr_length": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    line_ok = _rma(tr, int(p["atr_length"])).notna()     # the SuperTrend line exists (and is positive)
    n = int(p["rs_period"])
    ll, hh = c.rolling(n).min(), c.rolling(n).max()
    rs = (c - ll) / (hh - ll).where(hh > ll) * 100
    r = _rsi(c, int(p["rsi_period"]))
    t = float(p["rsi_threshold"])
    le = line_ok & (rs > 0) & (r > t)
    lx = (rs <= 0) & (r < t)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
