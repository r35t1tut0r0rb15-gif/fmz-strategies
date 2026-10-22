"""HPotter APO, daily bars: the EMA 10 above the EMA 20 holds long, below holds short; reversing on each change.
Port of FMZ strategy #442834 "基于双EMA价格摆动策略The-Dual-EMA-Price-Swing-Strategy" (Absolute Price Oscillator (APO) Backtest).

FMZ source id: 442834

Source
    https://www.fmz.com/strategy/442834 (PineScript v2, FMZ last modified 2024-02-26 13:52:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-226), EMA 10 / 20; reverse off
    xAPO = ema(close, 10) - ema(close, 20);  pos = xAPO > 0 ? 1 : xAPO < 0 ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level; the entries repeat while it holds and are refused while held.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA difference sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427479 (2 members, best partner #427479, Jaccard 0.756); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442834_hpotter_apo_sign_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 5],
    "long_len": [20, 50],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 20, "reverse": False}


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
    apo = (c.ewm(span=int(p["short_len"]), adjust=False).mean()
           - c.ewm(span=int(p["long_len"]), adjust=False).mean()).to_numpy()
    m = len(apo)
    pos = np.zeros(m, dtype=np.int8)
    s = 0
    for i in range(m):
        if apo[i] > 0:
            s = 1
        elif apo[i] < 0:
            s = -1
        pos[i] = s
    if p["reverse"]:
        pos = -pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(pos == 1, index=ix), false, pd.Series(pos == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
