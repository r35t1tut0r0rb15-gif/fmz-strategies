"""Run of same-colour candles, broker days: when the last 5 candles are all green, go long; when all red, go short (reversing); the position is closed 2 bars after the last signal. The investment value is a fixed notional.
Port of FMZ strategy #436604 "最后N只烛的逆向逻辑策略Last-N-Candle-Reverse-Logic-Strategy" (Last Number of Candles).

FMZ source id: 436604

Source
    https://www.fmz.com/strategy/436604 (PineScript v4, FMZ last modified 2023-12-26 11:00:29).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 148-215), candles to check 5, candles to exit 2, inverse logic off
    for i = 0 to n - 1: green candle -> consecutiveGreen += 1, consecutiveRed = 0; red candle -> consecutiveRed += 1, consecutiveGreen = 0  (var counters kept across bars; dojis change nothing)
    lastNCandlesGreen = consecutiveGreen >= n -> entry Buy (long), barsSinceEntry = 0;  lastNCandlesRed = consecutiveRed >= n -> entry Short, barsSinceEntry = 0;  barsSinceEntry += 1;  if barsSinceEntry >= 2: close Buy and Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two counters are `var`, so they carry from bar to bar; the counters are ported as written (a
      window of 5 candles without a red one adds 5 to the green count). With the inverse-logic switch
      off (fixed here), green buys and red shorts. The quantity (investment value / the first
      close) is sizing. REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour run.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the investment value and the quantity formula stored.
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

NAME = "fmz_436604_last_n_candles_run"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "num_check": [5, 3],
    "num_exit": [2, 3],
}
DEFAULT_PARAMS = {"num_check": 5, "num_exit": 2}


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
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    n_chk, n_exit = int(p["num_check"]), int(p["num_exit"])
    m = len(c)
    le, se, ex = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    green = red = 0
    since = 0
    for i in range(m):
        for k in range(n_chk):               # candle k bars back; missing history is neither colour
            j = i - k
            if j < 0:
                continue
            if c[j] > o[j]:
                green += 1
                red = 0
            elif c[j] < o[j]:
                red += 1
                green = 0
        if green >= n_chk:
            le[i] = True
            since = 0
        if red >= n_chk:
            se[i] = True
            since = 0
        since += 1
        ex[i] = since >= n_exit
    ix = bars_df.index
    exit_ = pd.Series(ex, index=ix)
    return pd.Series(le, index=ix), exit_, pd.Series(se, index=ix), exit_.copy()


def portfolio_kwargs(**params):
    return {}
