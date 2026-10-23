"""Two-hour bars, inverted: the chart EMA 28 crossing under the daily EMA 28 (last completed broker day) goes LONG, crossing over it goes SHORT, only on bars opening 09:00 to 23:00 UTC; reversing.
Port of FMZ strategy #438014 "Dual Moving Average Counter Trend Strategy" (gbpnzd 1h (SoftKill21)).

FMZ source id: 438014

Source
    https://www.fmz.com/strategy/438014 (PineScript v4, FMZ last modified 2024-01-08 11:01:11).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 176-268), MA type 2 = EMA, length 28; current resolution; daily ("D") copy; session 0900-2300; inverse on; exit off
    plot33 = ema(close, 28) (chart);  plot3 = security("D", ema(close, 28));  longC = crossover(plot33, plot3) and entrytime;  shortc = crossunder(plot33, plot3) and entrytime
    inverse: shortc -> entry long, longC -> entry short;  exit off (distance exits unused)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "inverse" is on by default, so a crossover of the chart EMA above the daily EMA sells and a
      crossunder buys, as written (weird case). The daily value is security("D", ...) without lookahead:
      on historical bars it is the last completed day's EMA (the day's own value only on its last bar);
      the port uses the last completed broker day throughout (as earlier ports). The session is read in
      UTC (header exchange time): bars opening 09:00 to 22:59. The volume EMA and the VWMA option are
      unused: volume is not used. The exits are off. The 2000 .. 2020 date filter is replaced by
      time_cond = true in the script. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, chart EMA against the daily EMA (inverted).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening 09:00 to 23:00 UTC (header exchange time); daily EMA of the last completed broker day.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438014_ema28_vs_daily_ema28_cross_inverted_2h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [28, 50],
    "inverse": [1, 0],
}
DEFAULT_PARAMS = {"length": 28, "inverse": 1, "sess_start": 9, "sess_end": 23}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    fast = c.ewm(span=n, adjust=False).mean()
    day = broker_day(c.index)
    dclose = c.groupby(day).last()
    demas = dclose.ewm(span=n, adjust=False).mean().shift(1)      # the last COMPLETED broker day
    slow = pd.Series(demas.reindex(day).to_numpy(), index=c.index)
    hr = c.index.hour
    sess = np.asarray((hr >= int(p["sess_start"])) & (hr < int(p["sess_end"])))
    up = ((fast > slow) & (fast.shift(1) <= slow.shift(1))).to_numpy() & sess
    dn = ((fast < slow) & (fast.shift(1) >= slow.shift(1))).to_numpy() & sess
    if int(p["inverse"]):
        le, se = dn, up
    else:
        le, se = up, dn
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
