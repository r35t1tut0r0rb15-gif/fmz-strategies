"""EMA 9 / 21 crossings with RSI, daily-EMA and MACD filters, daily bars: the cross up with RSI under 70, the close over the EMA 21 and MACD over its signal goes long, the mirror goes short; reversing. The ATR exits are armed only on bars with the opposite signal, which already reverses the position, so they never act.
Port of FMZ strategy #474876 "Multi Timeframe Trend Dynamic ATR Tracking Strategy" (TrenGuard Adaptive ATR Strategy).

FMZ source id: 474876

Source
    https://www.fmz.com/strategy/474876 (PineScript v5, FMZ last modified 2024-12-12 16:24:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-196), EMA 9 / 21; RSI 14, 70 / 30; ATR 14 x 2 / 2; "D" EMA 21 filter on; MACD 12 / 26 / 9; direction Both; 100 % of equity
    crossover(ema9, ema21) and rsi < 70 and close > emaD21 and macd > signal -> entry Long;  mirror -> entry Short;  long: exit(stop / limit = adaptive ATR levels, when = shortCondition);  short: exit(..., when = longCondition)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request equals the daily chart, so the filter is the chart's EMA 21. The exits are
      created only when the opposite condition holds (when=), and on those bars the opposite entry
      reverses the position at the next open, so the ATR levels never act: the port is the reversal on
      the entry signals. REVERSAL INTENDED. The equity share is not ported. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with RSI / EMA / MACD filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474876_ema9_21_cross_rsi_ema21_macd_filters_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21}


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
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70) & (c > b) & (macd > sig)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30) & (c < b) & (macd < sig)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
