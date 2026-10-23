"""Broker days, long only: volume above its 20-day average, RSI 14 crossing over 50, the close above the SMA 14 and the SMA 200 and an up day closing above a down day's open go long; nothing ever closes it (held to the end of the data, as written).
Port of FMZ strategy #473669 "Multi Technical Indicator Trend Following Trading Strategy" (Estrategia Completa - Volume, RSI e Tendencia).

FMZ source id: 473669

Source
    https://www.fmz.com/strategy/473669 (PineScript v5, FMZ last modified 2024-12-02 10:40:02).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-146), SMA 14 / 200; RSI 14 cross of 50; volume SMA 20; bullish engulfing (loose)
    buyCondition = volume > volumeMA and crossover(rsi, 50) and close > ma14 and bullishEngulfing and close > ma200 -> entry Compra
    bullishEngulfing = close > open and close[1] < open[1] and close > open[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script has no exit of any kind: the first qualifying day opens a long held to the end of the
      data, as written (as #458234). Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI 50 crossings in an uptrend on volume and engulfing candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473669_rsi50_cross_engulf_volume_sma200_no_exit_long_only"
FAMILY = "rsi_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 200}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    r = _rsi(c, 14)
    engulf = (c > o) & (c.shift(1) < o.shift(1)) & (c > o.shift(1))
    entry = ((v > v.rolling(20).mean()) & (r > 50) & (r.shift(1) <= 50) & (c > c.rolling(int(p["fast"])).mean())
             & engulf & (c > c.rolling(int(p["slow"])).mean()))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
