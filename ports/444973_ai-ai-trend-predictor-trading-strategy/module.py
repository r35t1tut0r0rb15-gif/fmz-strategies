"""Close crossings of the SMA 192 filtered by a range-autocorrelation score, daily bars: with the 10-bar share of positive range autocorrelations above 0.51, the close crossing over the SMA 192 goes long;
with it under 0.51, crossing under goes short; reversing.
Port of FMZ strategy #444973 "AI趋势预测交易策略AI-Trend-Predictor-Trading-Strategy" (AI Trend Predictor).

FMZ source id: 444973

Source
    https://www.fmz.com/strategy/444973 (PineScript v5, FMZ last modified 2024-03-15 16:06:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-213), lengths A 24 (unused), B 192, C 10; future length 5 (plot only)
    D = sma(correlation(high - low, (high - low)[1], 10) > 0 ? 1 : 0, 10);  D > 0.51 and crossover(close, sma(close, 192)) -> entry Buy;  D < 0.51 and crossunder(close, sma192) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.correlation is the rolling Pearson correlation of the bar range with its previous value over
      10 bars; a window where it is undefined counts as not positive (na > 0 is false). The "future
      close" is close[5], a past value, and only plots, as do C_close and the other unused lengths.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the "future" close is a past value and only plots.
    2 generic: PASS, SMA crossings with an autocorrelation filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_444973_sma192_cross_range_autocorr_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_b": [192, 100],
    "length_c": [10, 20],
}
DEFAULT_PARAMS = {"length_b": 192, "length_c": 10, "level": 0.51}


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
    nc = int(p["length_c"])
    rng = h - lo
    corr = rng.rolling(nc).corr(rng.shift(1))
    prob = (corr > 0).astype(float)
    d = prob.rolling(nc).mean()
    b = c.rolling(int(p["length_b"])).mean()
    c1, b1 = c.shift(1), b.shift(1)
    lv = float(p["level"])
    le = (d > lv) & (c > b) & (c1 <= b1)
    se = (d < lv) & (c < b) & (c1 >= b1)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
