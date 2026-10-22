"""Close crossing its SMA 60, daily bars: the close crossing over goes long, under goes short; the close 300 % above or 10 % below the fill closes either side (as written, on the price ratio for both);
reversing.
Port of FMZ strategy #442553 "基于MA线的趋势追踪策略Trend-Following-Strategy-Based-on-MA-Lines" (MA60 (long above, short below)).

FMZ source id: 442553

Source
    https://www.fmz.com/strategy/442553 (PineScript v5, FMZ last modified 2024-02-22 17:24:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-151), SMA 20 / 60 / 120 (trend plots only); take profit ratio >= 3, stop ratio <= -0.1
    crossover(close, ma60) -> entry Long;  crossunder(close, ma60) -> entry Short
    returns = close / position_avg_price - 1;  returns >= 3 -> close Long, close Short;  returns <= -0.1 -> close Long, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The return is the close over the average (fill) price, the same formula for both sides, so a
      short is closed when the price falls 10 % (its gain) or rises 300 %, as written; the tests run at
      the bar close from the bar the position is held at (na while flat). The SMA 20 / 120 trend only
      colours the chart. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings; closes against the fill price.
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

NAME = "fmz_442553_close_sma60_cross_fill_ratio_exits"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [60, 30],
    "stop_ratio": [0.1, 0.05],
}
DEFAULT_PARAMS = {"length": 60, "stop_ratio": 0.1, "target_ratio": 3.0}


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
    ma = c.rolling(int(p["length"])).mean()
    lg = ((c > ma) & (c.shift(1) <= ma.shift(1))).to_numpy()
    sh = ((c < ma) & (c.shift(1) >= ma.shift(1))).to_numpy()
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    tr_, sr = float(p["target_ratio"]), float(p["stop_ratio"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, fill = 0, np.nan
    for i in range(m):
        new = held
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if held != 0 and new == held:
            ret = cv[i] / fill - 1
            if ret >= tr_ or ret <= -sr:
                new = 0
        tgt[i] = new
        if new != held and new != 0 and i + 1 < m:
            fill = ov[i + 1]
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
