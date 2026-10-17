"""EMA 9 / 21 crosses confirmed by RSI 50 and MACD, broker days: EMA 9 crossing above EMA 21 with RSI 14 above 50 and
the MACD above its signal goes long; the bearish mirror closes the long and goes short.
Port of FMZ strategy #489198 "多重动量指标趋势追踪量化交易策略-Multi-Momentum-Indicator-Trend-Tracking-Quantitative-Trading-Strategy" (EMA + RSI + MACD Strategy).

FMZ source id: 489198

Source
    https://www.fmz.com/strategy/489198 (PineScript v6, FMZ last modified 2025-04-02 16:19:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 122-158), EMA 9 / 21, RSI 14, MACD 12 / 26 / 9
    bull = crossover(ema9, ema21) and rsi > 50 and macd > signal -> entry long
    bear = crossunder(ema9, ema21) and rsi < 50 and macd < signal -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close comes before the short entry: a stop-and-reverse. A short has no exit other than the next long
      (REVERSAL INTENDED). The RSI 70 / 30 inputs are unused.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs, RSI and MACD.
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

NAME = "fmz_489198_ema_9_21_cross_rsi_macd_reverse"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [9, 5],
    "ema_slow": [21, 50],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 21, "rsi_len": 14}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    bull = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (rsi > 50) & (macd > sig)).astype(bool)
    bear = ((ef < es) & (ef.shift(1) >= es.shift(1)) & (rsi < 50) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return bull, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
