"""ATR trailing-line flips, broker days: the close crossing over the ATR trailing line (key value 10 x ATR 10) goes long; crossing under it
goes short (reversing). The line is a signal line computed by the script, not a broker stop.
Port of FMZ strategy #435835 "Trend Tracking Strategy Based on Multi factor Model with Adaptive Trailing Stoploss" (TradersAI UT Bot).

FMZ source id: 435835

Source
    https://www.fmz.com/strategy/435835 (PineScript v2, FMZ last modified 2023-12-19 11:04:27).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 147-179), key value 10, ATR 10
    nLoss = a atr(c);  ts = close > ts[1] and close[1] > ts[1] ? max(ts[1], close - nLoss) : close < ts[1] and close[1] < ts[1] ? min(ts[1], close + nLoss) : close > ts[1] ? close - nLoss : close + nLoss
    buy = close > ts and crossover(ema(close, 1), ts);  sell = close < ts and crossover(ts, ema(close, 1));  buy -> entry long;  sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema(close, 1) is the close. The previous value is zero before the first bar (nz). The RSI,
      MACD and stochastic inputs are declared and unused. strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND435835 (2 members, best partner #439710, Jaccard 0.729); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435835_ut_bot_atr_line_flips"
FAMILY = "atr_trailing_line"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [10, 5],
    "c": [10, 20],
}
DEFAULT_PARAMS = {"a": 10, "c": 10}


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
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    n_loss = (float(p["a"]) * tr.ewm(alpha=1 / int(p["c"]), adjust=False).mean()).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        prev = 0.0 if i == 0 or np.isnan(ts[i - 1]) else ts[i - 1]
        cp = cv[i - 1] if i > 0 else np.nan
        if cv[i] > prev and cp > prev:
            ts[i] = np.maximum(prev, cv[i] - n_loss[i])
        elif cv[i] < prev and cp < prev:
            ts[i] = np.minimum(prev, cv[i] + n_loss[i])
        elif cv[i] > prev:
            ts[i] = cv[i] - n_loss[i]
        else:
            ts[i] = cv[i] + n_loss[i]
    t = pd.Series(ts, index=c.index)
    above = (c > t) & (c.shift(1) <= t.shift(1))
    below = (t > c) & (t.shift(1) <= c.shift(1))
    le = ((c > t) & above).fillna(False).astype(bool)
    se = ((c < t) & below).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
