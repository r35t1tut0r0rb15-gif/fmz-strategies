"""Daily close direction with a Hull-style WMA turn, daily bars: the close above the previous close with the fast Hull line above its value two bars back goes long, both down goes short; reversing (the
profit-gated closes repeat the reversals).
Port of FMZ strategy #442817 "双移动平均-HullMA交叉趋势策略Dual-Moving-Average-HullMA-Crossover-Trend-Strategy" (ZendicatoR).

FMZ source id: 442817

Source
    https://www.fmz.com/strategy/442817 (PineScript v2, FMZ last modified 2024-02-26 11:21:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-155), double HullMA 7; WMA 34 / 144 / 377 (plots only); decision threshold (unused); TP 4200 $
    A = security(D, close), B = security(D, close[1]) (the daily chart's own closes);  n1 = wma(2 wma(close, 4) - wma(close, 7), 3);  n2 = the same on close[2]
    A > B and n1 > n2 -> entry Long;  A < B and n1 < n2 -> entry Short;  A < B and n2 > n1 and openprofit > 4200 -> close Long;  A > B and n1 > n2 and openprofit > 4200 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily chart the daily requests return the chart's own close and previous close. Each close
      condition is the opposite entry's condition plus a profit test, so it only repeats the reversal
      that entry makes, and the cash profit test never changes a position: no profit test is ported.
      round(7 / 2) = 4 and round(sqrt(7)) = 3 as in Pine. The WMA plots and the threshold are unused.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close direction with a Hull turn.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG442817 (2 members, best partner #436646, Jaccard 0.850); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442817_close_direction_hull_turn_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [7, 14],
}
DEFAULT_PARAMS = {"keh": 7}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _pine_round(x):
    return int(np.floor(x + 0.5))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    k = int(p["keh"])
    diff = 2 * _wma(c, _pine_round(k / 2)) - _wma(c, k)
    n1 = _wma(diff, _pine_round(np.sqrt(k)))
    n2 = n1.shift(2)
    up, dn = c > c.shift(1), c < c.shift(1)
    le = up & (n1 > n2)
    se = dn & (n1 < n2)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
