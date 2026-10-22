"""Crossings of an EMA 50 and a WMA 100 of RSI 14, broker days, long only: the EMA crossing over the WMA buys, crossing under closes.
Port of FMZ strategy #478734 "多均线交叉辅助RSI动态参数量化交易策略-Dynamic-RSI-Quantitative-Trading-Strategy-with-Multiple-Moving-Average-Crossover" (RSI-MA Strategy).

FMZ source id: 478734

Source
    https://www.fmz.com/strategy/478734 (PineScript v6, FMZ last modified 2025-01-17 16:14:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-269), RSI 14; MA1 SMA 20, MA2 EMA 50, MA3 WMA 100 of the RSI (defaults); divergence off
    crossover(ema(rsi, 50), wma(rsi, 100)) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default MA types are ported (MA2 EMA, MA3 WMA). The divergence code is off by default and only
      labels. Long only. The 200 % of equity size is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI moving-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_478734_rsi14_ema50_wma100_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma2_length": [50, 20],
    "ma3_length": [100, 50],
}
DEFAULT_PARAMS = {"ma2_length": 50, "ma3_length": 100, "rsi_length": 14}


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
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0).where(dn != 0, 100.0)        # down == 0 ? 100 : up == 0 ? 0 : rsi
    return rsi.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    a = r.ewm(span=int(p["ma2_length"]), adjust=False).mean()
    b = _wma(r, int(p["ma3_length"]))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    lx = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
