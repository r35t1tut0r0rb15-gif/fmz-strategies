"""EMA 20 against SMA 20 crossings, broker days: the EMA crossing over the SMA with the close above the EMA goes long, crossing under with the close under it goes short; a crossing that fails the close test
only closes the opposite position.
Port of FMZ strategy #437693 "基于EMA和SMA均线交叉的趋势反转策略Trend-Reversal-Strategy-Based-on-EMA-and-SMA-Crossover" (EMA-SMA Crossover Strategy).

FMZ source id: 437693

Source
    https://www.fmz.com/strategy/437693 (PineScript v5, FMZ last modified 2024-01-04 17:59:04).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 142-170), EMA 20, SMA 20 (fixed in the code)
    buy = crossover(ema, sma) and close > ema -> entry Buy;  sell = crossunder(ema, sma) and close < ema -> entry Sell;  crossunder -> close Buy;  crossover -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Orders follow the script's call order (entries, then the closes of the position open at the bar's
      close and left unchanged by the entries). REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437693_ema_sma_cross_close_filter"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [20, 10],
    "sma_length": [20, 40],
}
DEFAULT_PARAMS = {"ema_length": 20, "sma_length": 20}


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
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    s = c.rolling(int(p["sma_length"])).mean()
    xo = ((e > s) & (e.shift(1) <= s.shift(1))).to_numpy()
    xu = ((e < s) & (e.shift(1) >= s.shift(1))).to_numpy()
    cv, ev = c.to_numpy(dtype=float), e.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s_, changed = pos, False
        if xo[i] and cv[i] > ev[i] and s_ != 1:
            s_, changed = 1, True
        if xu[i] and cv[i] < ev[i] and s_ != -1:
            s_, changed = -1, True
        if not changed:
            if xu[i] and pos == 1:
                s_ = 0
            elif xo[i] and pos == -1:
                s_ = 0
        if s_ == 1 and pos != 1:
            le[i] = True
        elif s_ == -1 and pos != -1:
            se[i] = True
        elif s_ == 0 and pos == 1:
            lx[i] = True
        elif s_ == 0 and pos == -1:
            sx[i] = True
        pos = s_
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
