"""Lows-based multi-filter entries, broker days: a close over the SMA 25 of lows and the EMA 200 of lows, inside the Keltner channel of lows, with a negative MACD histogram and the stochastic under 50 goes
long; the mirror goes short (reversing).
Port of FMZ strategy #436219 "Quantitative Trading Price Breakthrough Strategy" (Scalping Trading System Crypto and Stocks).

FMZ source id: 436219

Source
    https://www.fmz.com/strategy/436219 (PineScript v5, FMZ last modified 2023-12-22 12:42:15).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 119-169), source = low; SMA 25, EMA 200; Keltner 10 / ATR 14 x 2; MACD 4 / 34 / 5 (EMAs); stochastic 10
    long = close > sma(low, 25) and close < upper and close > lower and hist < 0 and k < 50 and close > ema(low, 200);  short = close < sma(low, 25) and close < upper and close > lower and hist > 0 and k > 50 and close < ema(low, 200)
    upper / lower = sma(low, 10) +- 2 atr(14);  hist from the MACD of the LOW;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages, the channel and the MACD all read the LOW price, as written. The conditions are
      states re-sent every bar; vbt ignores a same-side signal. strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, averages, a channel and an oscillator filter.
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

NAME = "fmz_436219_lows_based_filters"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [25, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"len": 25, "len2": 200, "mult": 2.0, "lengthk": 10, "atr_len": 14, "period_k": 10, "fast": 4, "slow": 34, "signal": 5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    out = lo.rolling(int(p["len"])).mean()
    out2 = lo.ewm(span=int(p["len2"]), adjust=False).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    ma = lo.rolling(int(p["lengthk"])).mean()
    upper, lower = ma + atr * float(p["mult"]), ma - atr * float(p["mult"])
    n = int(p["period_k"])
    with np.errstate(invalid="ignore", divide="ignore"):
        k = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    macd = lo.ewm(span=int(p["fast"]), adjust=False).mean() - lo.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = ((c > out) & (c < upper) & (c > lower) & (hist < 0) & (k < 50) & (c > out2)).fillna(False).astype(bool)
    se = ((c < out) & (c < upper) & (c > lower) & (hist > 0) & (k > 50) & (c < out2)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
