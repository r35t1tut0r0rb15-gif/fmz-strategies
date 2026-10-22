"""Two EMA crossing pairs, daily bars: the EMA 21 crossing over the EMA 55, or the EMA 55 over the EMA 200, goes long; the crossings down go short; reversing (on a bar with crossings both ways the later call, the 55 / 200 one, wins).
Port of FMZ strategy #457796 "多重EMA交叉趋势跟踪策略Multi-EMA-Crossover-Trend-Following-Strategy" (EMA Crossover Strategy (21 / 55 and 55 / 200)).

FMZ source id: 457796

Source
    https://www.fmz.com/strategy/457796 (PineScript v5, FMZ last modified 2024-07-26 16:24:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-216), EMA 21 / 55 / 100 / 200 (100 plotted only)
    crossover(ema21, ema55) -> entry Long;  crossunder -> entry Short;  crossover(ema55, ema200) -> entry longCondition2;  crossunder -> entry shortCondition2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second pair uses other ids, but pyramiding 1 refuses a same-side entry with any id, so each
      crossing either opens, reverses or is ignored. On a bar with an up and a down crossing the
      later call wins (as #437773). REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two EMA crossing pairs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_457796_ema21_55_and_55_200_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 9],
    "mid": [55, 50],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 21, "mid": 55, "slow": 200}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    md = c.ewm(span=int(p["mid"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()

    def over(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()

    calls = [(over(f, md), 1), (over(md, f), -1), (over(md, s), 1), (over(s, md), -1)]
    m = len(c)
    want = np.zeros(m, dtype=int)
    for arr, d in calls:
        want = np.where(arr, d, want)        # the later call wins a tie
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(want == 1, index=ix), false, pd.Series(want == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
