"""HPotter Mass Index, daily bars: the 25-bar sum of the ratio of the range's EMA 9 to its double EMA 9 above 26.5 holds short, below holds long; reversing.
Port of FMZ strategy #442924 "Short term Trading Strategy Based on Momentum Indicator" (MASS Index).

FMZ source id: 442924

Source
    https://www.fmz.com/strategy/442924 (PineScript v2, FMZ last modified 2024-02-27 14:07:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 126-161), lengths 9 / 25; trigger 26.5; reverse off
    xEMA = ema(high - low, 9);  nRes = sum(xEMA / ema(xEMA, 9), 25);  pos = nRes > 26.5 ? -1 : nRes < 26.5 ? 1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level; the entries repeat while it holds and are refused while held.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Mass Index against a trigger.
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

NAME = "fmz_442924_hpotter_mass_index_trigger_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length2": [25, 50],
    "trigger": [26.5, 27.0],
}
DEFAULT_PARAMS = {"length2": 25, "trigger": 26.5, "length1": 9, "reverse": False}


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
    h, lo = bars_df["high"], bars_df["low"]
    n1 = int(p["length1"])
    xe = (h - lo).ewm(span=n1, adjust=False).mean()
    xs = xe.ewm(span=n1, adjust=False).mean()
    ratio = (xe / xs).where(xs != 0, 0.0)
    res = ratio.rolling(int(p["length2"])).sum().to_numpy()
    tr_ = float(p["trigger"])
    m = len(res)
    pos = np.zeros(m, dtype=np.int8)
    s = 0
    for i in range(m):
        if res[i] > tr_:
            s = -1
        elif res[i] < tr_:
            s = 1
        pos[i] = s
    if p["reverse"]:
        pos = -pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(pos == 1, index=ix), false, pd.Series(pos == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
