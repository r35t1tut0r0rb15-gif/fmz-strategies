"""RSI of a 200-bar regression line against its EMA, long only, broker days: the RSI 21 of linreg(close, 200) crossing over its EMA 50 goes long, crossing under closes.
Port of FMZ strategy #439839 "基于线性回归RSI的量化交易策略Quantitative-Trading-Strategy-Based-on-Linear-Regression-RSI" (Linear RSI).

FMZ source id: 439839

Source
    https://www.fmz.com/strategy/439839 (PineScript v4, FMZ last modified 2024-01-24 11:35:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-173), LR 200; RSI 21; EMA 50; levels 50 / 50; first logic on, second off; test period true
    Lr = linreg(close, 200, 0);  rsi = rsi(Lr, 21);  ema = ema(rsi, 50);  crossover(rsi, ema) -> entry BUY;  crossunder(rsi, ema) -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the first logic is on. The entry and the close cannot share a bar. Long only. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI of a regression line and its EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439839_linear_regression_rsi_ema_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [200, 100],
    "ema_fast": [50, 20],
}
DEFAULT_PARAMS = {"length": 200, "ema_fast": 50, "length2": 21}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _linreg(y, n):
    """Pine's linreg(y, n, 0): the least-squares line over the last n bars, read at the newest bar."""
    k = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sky = (k * y).rolling(n).sum()
    x0 = k - (n - 1)                                   # x = k - x0 runs 0 .. n-1 inside the window
    sxy = sky - x0 * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(_linreg(c, int(p["length"])), int(p["length2"]))
    e = r.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    up = (r > e) & (r.shift(1) <= e.shift(1))
    dn = (r < e) & (r.shift(1) >= e.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
