"""Agreement of a Coral trend (close vs EMA 14 of hlc3) and a Donchian 20 trend (closes beyond the previous channel), broker days: both turning up goes long, both down goes short, once per state change; reversing.
Port of FMZ strategy #478743 "Adaptive Trend Following and Multi Confirmation Trading Strategy" (Coral Tides Strategy).

FMZ source id: 478743

Source
    https://www.fmz.com/strategy/478743 (PineScript v5, FMZ last modified 2025-01-17 16:29:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-156), Donchian 20; Coral EMA 14 of hlc3
    coral = close > ema(hlc3, 14) ? 1 : close < it ? -1 : coral[1];  donch = close > highest(high, 20)[1] ? 1 : close < lowest(low, 20)[1] ? -1 : donch[1]
    coral == 1 and donch == 1 and state != 1 -> buy, state := 1;  both -1 and state != -1 -> sell, state := -1;  buy -> entry Long;  sell -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both trends keep their last value when the close is neither side, and the state machine fires
      each signal once per change, as written (a loop). REVERSAL INTENDED. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Coral and Donchian trend agreement.
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

NAME = "fmz_478743_coral14_donchian20_trend_agree_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dlen": [20, 55],
    "coral_period": [14, 30],
}
DEFAULT_PARAMS = {"dlen": 20, "coral_period": 14}


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


def _kept_trend(up, dn):
    """trend := up ? 1 : dn ? -1 : trend[1] (0 before the first)."""
    out = np.zeros(len(up))
    t = 0.0
    for i in range(len(up)):
        if up[i]:
            t = 1.0
        elif dn[i]:
            t = -1.0
        out[i] = t
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    coral = ((h + lo + c) / 3).ewm(span=int(p["coral_period"]), adjust=False).mean()
    ct = _kept_trend((c > coral).to_numpy(), (c < coral).to_numpy())
    n = int(p["dlen"])
    hh, ll = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    dt = _kept_trend((c > hh).to_numpy(), (c < ll).to_numpy())
    m = len(ct)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state = 0
    for i in range(m):
        if ct[i] == 1 and dt[i] == 1 and state != 1:
            le[i], state = True, 1
        elif ct[i] == -1 and dt[i] == -1 and state != -1:
            se[i], state = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
