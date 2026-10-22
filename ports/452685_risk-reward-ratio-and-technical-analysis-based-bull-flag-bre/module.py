"""Bull-flag breakouts, daily bars, long only (spot): a close over the previous high while that high is under the 5-bar high buys, with a stop just under the 5-bar low and a target 3 times the risk.
Port of FMZ strategy #452685 "Risk Reward Ratio and Technical Analysis Based Bull Flag Breakout Strategy" (Bull Flag Breakout).

FMZ source id: 452685

Source
    https://www.fmz.com/strategy/452685 (PineScript v5, FMZ last modified 2024-05-28 10:47:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-123), flag length 5; stop buffer 0.01 (price); risk-reward 3; 10 % of equity
    high[1] < highest(high, 5) and close > high[1] -> entry Bull Flag Long, exit(limit = close + 3 x (close - stop)), exit(stop = lowest(low, 5) - 0.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are fixed on the signal bar from its close: ported as fractions of the
      signal close, the stop distance (close - (low5 - 0.01)) / close and the target 3 times it, read
      at the fill bar from the signal bar (known at the fill's open). A repeat signal inside the trade
      re-issues both exits from that bar, which stops() cannot express: the port keeps the opening
      levels and marks trailing_stop_pending (as #434428). Spot account: Long only. Stops on 1-day
      bars: mark coarse_bar_stop. The 10 % of equity is sizing. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-bar levels as fractions; re-issued exits pending (mark).
    2 generic: PASS, flag breakouts with a 3R target.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452685_bull_flag_breakout_3r_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "flag_len": [5, 10],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"flag_len": 5, "rr": 3.0, "buffer": 0.01}


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


def _flag(bars_df, p):
    n = int(p["flag_len"])
    h, c = bars_df["high"], bars_df["close"]
    return (h.shift(1) < h.rolling(n).max()) & (c > h.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    false = pd.Series(False, index=bars_df.index)
    return _flag(bars_df, p), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    stop = bars_df["low"].rolling(int(p["flag_len"])).min() - float(p["buffer"])
    dist = ((c - stop) / c).where(_flag(bars_df, p))
    sl = dist.shift(1)
    return {"sl_stop": sl, "tp_stop": sl * float(p["rr"])}


def portfolio_kwargs(**params):
    return {}
