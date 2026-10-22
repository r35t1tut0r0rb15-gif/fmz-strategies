"""RSI-extreme engulfing candles, long only, broker days: a bullish engulfing close with the RSI 14 at or under 30 on this or the previous bar goes long; a bearish engulfing close with the RSI at or over 70 on
this or the previous bar closes.
Port of FMZ strategy #439603 "低风险DCA趋势交易策略Low-Risk-DCA-Trend-Trading-Strategy" (Phil's Pine Scripts - low risk long DCA Trend trade).

FMZ source id: 439603

Source
    https://www.fmz.com/strategy/439603 (PineScript v4, FMZ last modified 2024-01-22 10:20:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-160), RSI 14 of close, overbought 70, oversold 30; 50000 per trade
    bullishEC = close > open[1] and close[1] < open[1];  bearishEC = close < open[1] and close[1] > open[1]
    (rsiOS or rsiOS[1]) and bullishEC -> entry OL;  (rsiOB or rsiOB[1]) and bearishEC -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * One position is held (pyramiding 1); the two setups cannot share a bar (the previous candle's
      colour). Long only. The cash-per-trade quantity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes and engulfing closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash-per-trade quantity stored.
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

NAME = "fmz_439603_rsi_extreme_engulfing_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "rsi_oversold": [30, 40],
}
DEFAULT_PARAMS = {"rsi_length": 14, "rsi_oversold": 30, "rsi_overbought": 70}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    os_ = r <= float(p["rsi_oversold"])
    ob = r >= float(p["rsi_overbought"])
    bull = (c > o.shift(1)) & (c.shift(1) < o.shift(1))
    bear = (c < o.shift(1)) & (c.shift(1) > o.shift(1))
    le = (os_ | os_.shift(1, fill_value=False)) & bull
    lx = (ob | ob.shift(1, fill_value=False)) & bear
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
