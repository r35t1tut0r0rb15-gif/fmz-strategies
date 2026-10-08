"""Combo 123 Reversal & Elder Ray bear power (HPotter): long when the 123-reversal state and the
"day high minus EMA 13" state are both +1, short when both are -1, flat otherwise.
Port of FMZ strategy #426498 "Multi factor Combined Trading Strategy".

Source
    https://www.fmz.com/strategy/426498 (PineScript v4, FMZ last modified 2023-09-12 16:05:10).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 137-176), 14 / 1 / 3 / 50, LengthBP 13, Trigger 0
    vFast = sma(stoch(close, high, low, 14), 1); vSlow = sma(vFast, 3)
    pos123 = +1 if close[2] < close[1] < close and vFast < vSlow and vFast > 50,
             -1 if close[2] > close[1] > close and vFast > vSlow and vFast < 50, else previous
    DayHigh = new day ? high : max(high, DayHigh[1]);  nRes = DayHigh - ema(close, 13)
    posBP = nRes > Trigger ? 1 : nRes < Trigger ? -1 : previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * On daily bars every bar starts a new day, so DayHigh is the bar's high.
    * Criterion 2: Trigger is in price units; its default 0 is 0 in any unit (kept fixed).
    * "Trade reverse" off (source default). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426498_combo_123_reversal_bear_power"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "length_bp": [13, 21],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_length": 3, "level": 50, "length_bp": 13}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def _state(up, dn):
    out = np.zeros(len(up))
    prev = 0.0
    for i in range(len(up)):
        prev = 1.0 if up[i] else (-1.0 if dn[i] else prev)
        out[i] = prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    fast = (100 * (c - lo) / (hi - lo)).rolling(int(p["k_smooth"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    a = _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > p["level"])).to_numpy(),
               ((c2 > c1) & (c < c1) & (fast > slow) & (fast < p["level"])).to_numpy())
    res = h - c.ewm(span=int(p["length_bp"]), adjust=False).mean()
    b = _state((res > 0).to_numpy(), (res < 0).to_numpy())
    target = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
