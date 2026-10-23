"""Broker days: EMA 9 above EMA 21 with RSI 14 under 50, a positive MACD histogram, the stochastic %K 3 of 14 under 80 and Ichimoku span A above span B goes long; the mirror (RSI over 50, negative histogram, %K over 20, span A under B) goes short; each signal closes the other side; reversing.
Port of FMZ strategy #491042 "Multi Indicator Dynamic Position Size Volatility Adaptive Quantitative Trading Strategy" (Phoenix Master Strategy (PMI)).

FMZ source id: 491042

Source
    https://www.fmz.com/strategy/491042 (PineScript v5, FMZ last modified 2025-04-18 09:55:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 172-275), "D" EMA 9 / 21 on a 1d chart; RSI 14 (50); MACD 12 / 26 / 9 histogram; stoch 14, %K 3; Ichimoku 9 / 26 / 52 (spans undisplaced); volume, pivots, sentiment and position size drawn only
    longSignal = ema9 > ema21 and rsi < 50 and macdHist > 0 and stochK < 80 and spanA > spanB;  shortSignal = ema9 < ema21 and rsi > 50 and macdHist < 0 and stochK > 20 and spanA < spanB
    entry AL when longSignal, close AL when shortSignal;  entry SAT when shortSignal, close SAT when longSignal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" security runs on the header's 1-day chart, so it is the chart's own EMA (no delay). Close
      then enter on the opposite signal is a reversal; there is no other exit. The spans are compared
      where they are computed (not displaced 26 bars). The volume explosion, pivots, "sentiment" and
      liquidity heat map are drawn or alerted only, so volume is not used. The risk-based position size is
      only plotted. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend with momentum pullback filters and the Ichimoku cloud.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (position size plotted only).
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

NAME = "fmz_491042_ema9_21_rsi_macd_stoch_ichimoku_cloud_reversal"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [9, 12],
    "ema_slow": [21, 26],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 21}


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


def _mid(h, lo, n):
    return (h.rolling(n).max() + lo.rolling(n).min()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e1 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    k = (100 * (c - ll) / (hh - ll).where(hh != ll)).rolling(3).mean()
    tenkan, kijun = _mid(h, lo, 9), _mid(h, lo, 26)
    span_a, span_b = (tenkan + kijun) / 2, _mid(h, lo, 52)
    le = (e1 > e2) & (r < 50) & (hist > 0) & (k < 80) & (span_a > span_b)
    se = (e1 < e2) & (r > 50) & (hist < 0) & (k > 20) & (span_a < span_b)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
