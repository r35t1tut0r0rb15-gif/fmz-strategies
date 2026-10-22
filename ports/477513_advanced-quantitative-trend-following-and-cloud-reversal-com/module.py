"""EMA 9 / 21 cross-ups go long; SMA "Tenkan 9 / Kijun 26" cross-downs with the close under both SMA spans go short, broker days; reversing. The 1.5 % / 3 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #477513 "Advanced Quantitative Trend Following and Cloud Reversal Composite Trading Strategy" (EMA Crossover Buy + Ichimoku Cloud Sell Strategy).

FMZ source id: 477513

Source
    https://www.fmz.com/strategy/477513 (PineScript v5, FMZ last modified 2025-01-06 10:56:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 75-149), EMA 9 / 21; Tenkan / Kijun / span B as SMAs 9 / 26 / 52 of the close; span A = SMA 2 of (Tenkan + Kijun); stop 1.5 %, target 3 % of the current close
    crossover(ema9, ema21) -> entry Buy;  crossunder(sma9, sma26) and close < sma(sma9 + sma26, 2) and close < sma52 -> entry Sell;  every bar: exit(Buy / Sell, stop = close x (1 -/+ 1.5 %), limit = close x (1 +/- 3 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Ichimoku lines are simple moving averages of the close, as written, and span A is the 2-bar SMA
      of the SUM of Tenkan and Kijun (not their average); the spans are read at the current bar, the
      displacement only shifts the plots. The bracket is re-sent on every bar from that bar's close, so
      its levels move after entry: stops() cannot express a level re-set every bar, so it is described
      here and kept pending (as #438034, mark trailing_stop_pending). On a bar with both signals the later
      short call wins (#437773). REVERSAL INTENDED. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, EMA cross-ups and SMA-Ichimoku cross-downs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477513_ema9_21_crossup_sma_ichimoku_crossdown_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [9, 5],
    "kijun": [26, 50],
}
DEFAULT_PARAMS = {"short_ema": 9, "long_ema": 21, "tenkan": 9, "kijun": 26, "span_b": 52}


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
    c = bars_df["close"]
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    tk = c.rolling(int(p["tenkan"])).mean()
    kj = c.rolling(int(p["kijun"])).mean()
    span_a = (tk + kj).rolling(2).mean()
    span_b = c.rolling(int(p["span_b"])).mean()
    le = (es > el) & (es.shift(1) <= el.shift(1))
    se = (tk < kj) & (tk.shift(1) >= kj.shift(1)) & (c < span_a) & (c < span_b)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
