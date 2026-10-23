"""Broker days: EMA 5 > 14 > 34 > 55 with the close above the EMA 34, a positive MACD histogram, RSI 14 over 50 and volume over 1.5 x its 20-day average goes long; the mirror goes short; the opposite signal reverses.
Port of FMZ strategy #481098 "Multi Moving Average and Indicator Cross Trend Following Quantitative Trading System" (Advanced EMA + MACD + RSI Strategy with Support/Resistance).

FMZ source id: 481098

Source
    https://www.fmz.com/strategy/481098 (PineScript v5, FMZ last modified 2025-02-08 14:58:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 99-154), EMA 5 / 14 / 34 / 55; MACD 12 / 26 / 9; RSI 14; volume SMA 20 x 1.5
    longCondition = ema5 > ema14 > ema34 > ema55 and close > ema34 and macdHist > 0 and rsi > 50 and volume > avgVolume x 1.5 -> entry Long;  shortCondition mirrored -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only, as states; an entry while in that position adds nothing and an opposite entry
      reverses. The 20-bar high / low only plot. REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked-EMA trend with MACD, RSI and volume confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481098_ema_stack_macd_rsi_volume_state_reversal"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_mult": [1.5, 1.0],
    "rsi_mid": [50.0, 55.0],
}
DEFAULT_PARAMS = {"vol_mult": 1.5, "rsi_mid": 50.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    e5, e14, e34, e55 = (c.ewm(span=n, adjust=False).mean() for n in (5, 14, 34, 55))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    mid = float(p["rsi_mid"])
    buy = (e5 > e14) & (e14 > e34) & (e34 > e55) & (c > e34) & (hist > 0) & (r > mid) & vol_ok
    sell = (e5 < e14) & (e14 < e34) & (e34 < e55) & (c < e34) & (hist < 0) & (r < 100 - mid) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
