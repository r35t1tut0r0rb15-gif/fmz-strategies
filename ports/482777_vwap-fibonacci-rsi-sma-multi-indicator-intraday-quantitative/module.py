"""Broker days: the close crossing over its SMA 9 goes long; the close crossing under the SMA 9, or RSI 14 crossing under 70 with the close inside its own bar's 38.2-61.8 % range, goes short; the opposite signal reverses.
Port of FMZ strategy #482777 "多指标整合日内量化交易策略基于VWAP-Fibonacci-RSI-SMA的动态信号系统-Multi-Indicator-Intraday-Quantitative-Trading-Strategy-Dynamic-Signal-System-Based-on-VWAP-Fibonacci-RSI-SMA" (Intraday Strategy with VWAP, Fibonacci, RSI, and SMA).

FMZ source id: 482777

Source
    https://www.fmz.com/strategy/482777 (PineScript v5, FMZ last modified 2025-02-27 17:50:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 101-148), RSI 14 (30 / 70); SMA 9; Fibonacci levels of the bar's own high / low; VWAP on the chart timeframe
    upper = high - 0.382 x (high - low);  lower = high - 0.618 x (high - low)  (security of the chart's own high / low);  price_above_vwap = close > request.security(tf "", ta.vwap(close))
    finalBuySignal = (crossover(rsi, 30) and lower < close < upper and price_above_vwap) or crossover(close, sma9) -> entry Buy
    finalSellSignal = (crossunder(rsi, 70) and lower < close < upper and not price_above_vwap) or crossunder(close, sma9) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the header's 1-day bars ta.vwap(close) is the bar's own close, so price_above_vwap is never
      true: the RSI buy branch can never fire and the RSI sell branch only needs its RSI and range tests
      (weird case; volume is therefore not used, held for volume). The "Fibonacci" levels are the current
      bar's own range. Entries only; an opposite entry reverses (both on one bar: the later sell wins).
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA 9 crossings with an RSI-70 sell branch.
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

NAME = "fmz_482777_close_sma9_cross_rsi70_range_sell_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [9, 20],
    "rsi_hi": [70.0, 65.0],
}
DEFAULT_PARAMS = {"sma_len": 9, "rsi_hi": 70.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, 14)
    sma = c.rolling(int(p["sma_len"])).mean()
    upper, lower = h - (h - lo) * 0.382, h - (h - lo) * 0.618
    hi = float(p["rsi_hi"])
    rsi_sell = (r < hi) & (r.shift(1) >= hi) & (c < upper) & (c > lower)   # "not above the VWAP" always holds
    sell = rsi_sell | ((c < sma) & (c.shift(1) >= sma.shift(1)))
    buy = (c > sma) & (c.shift(1) <= sma.shift(1)) & ~sell
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
