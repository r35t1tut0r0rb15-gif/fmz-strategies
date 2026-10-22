"""EMA 20 / 50 crossings with RSI 14 beyond 50, the MACD 12 / 26 / 9 side and the EMA 200 side, broker days, long only: a confirmed up-cross goes long, a confirmed down-cross closes.
Port of FMZ strategy #484595 "Multi Indicator Trend Confirmation Momentum Trading Strategy" (Best Forex Strategy).

FMZ source id: 484595

Source
    https://www.fmz.com/strategy/484595 (PineScript v5, FMZ last modified 2025-03-03 10:35:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-223), EMA 20 / 50 / 100 (plot) / 200; RSI 14; MACD 12 / 26 / 9; Fibonacci 50-bar levels (plots only)
    crossover(ema20, ema50) and rsi > 50 and macd > signal and close > ema200 -> entry Long
    crossunder(ema20, ema50) and rsi < 50 and macd < signal and close < ema200 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Fibonacci levels and labels are drawing only. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with RSI / MACD / EMA 200 confirmation.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_484595_ema20_50_cross_rsi_macd_ema200_confirm_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s, e200 = ema(p["fast"]), ema(p["slow"]), ema(200)
    r = _rsi(c, 14)
    macd = ema(12) - ema(26)
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50) & (macd > sig) & (c > e200)
    lx = (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50) & (macd < sig) & (c < e200)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
