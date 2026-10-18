"""Stochastic RSI with a relative vigor index, broker days: a bar with K at or over D under 30 and the vigor index turning up
through its signal is an up event, the mirror over 70 a down event; the position follows the latest event (long after an up
event, short after a down event, reversing).
Port of FMZ strategy #435463 "基于Stochastic-RSI的数字货币交易策略Stochastic-RSI-Strategy-for-Cryptocurrency-Trading" (Stochastic RSI).

FMZ source id: 435463

Source
    https://www.fmz.com/strategy/435463 (PineScript v4, FMZ last modified 2023-12-15 10:08:14).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 153-188), RSI 14, stoch 14 of the RSI, K = SMA 3, D = SMA 3; relative vigor index 5 with a 4-bar weighted signal
    Dn = K <= D and K > 70 and rvi <= sig and rvi[1] >= sig[1];  Up = K >= D and K < 30 and rvi >= sig and rvi[1] <= sig[1]
    long = crossover(Up, Dn);  short = crossunder(Up, Dn);  last_long = long ? time : nz(last_long[1]);  last_short = short ? time : nz(last_short[1])
    crossover(last_long, last_short) -> entry long;  crossover(last_short, last_long) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Up and Dn are 1 / 0 numbers and cannot both be 1, so an up event is Up turning on, a down event
      Dn turning on. The time stamps make the entry fire when the latest event changes side (a
      second event of the same side adds nothing). The vigor index uses Pine's symmetrical weighted
      average swma (weights 1, 2, 2, 1 over 6). strategy.entry reverses: REVERSAL INTENDED. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator events.
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

NAME = "fmz_435463_stoch_rsi_vigor_events"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [5, 10],
    "length_rsi": [14, 21],
}
DEFAULT_PARAMS = {"per": 5, "length_rsi": 14, "length_stoch": 14, "smooth_k": 3, "smooth_d": 3}


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


def _swma(s):
    return (s.shift(3) + 2 * s.shift(2) + 2 * s.shift(1) + s) / 6


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length_rsi"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    ls = int(p["length_stoch"])
    with np.errstate(invalid="ignore", divide="ignore"):
        st = 100 * (rsi - rsi.rolling(ls).min()) / (rsi.rolling(ls).max() - rsi.rolling(ls).min())
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    per = int(p["per"])
    with np.errstate(invalid="ignore", divide="ignore"):
        rvi = _swma(c - o).rolling(per).sum() / _swma(h - lo).rolling(per).sum()
    sig = _swma(rvi)
    dn_ev = ((k <= d) & (k > 70) & (rvi <= sig) & (rvi.shift(1) >= sig.shift(1))).to_numpy()
    up_ev = ((k >= d) & (k < 30) & (rvi >= sig) & (rvi.shift(1) <= sig.shift(1))).to_numpy()
    upv, dnv = up_ev.astype(int), dn_ev.astype(int)
    u1, d1 = np.concatenate(([0], upv[:-1])), np.concatenate(([0], dnv[:-1]))
    long_ev = (upv > dnv) & (u1 <= d1)
    short_ev = (upv < dnv) & (u1 >= d1)
    m = len(upv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = 0
    for i in range(m):
        if long_ev[i] and last != 1:
            le[i], last = True, 1
        elif short_ev[i] and last != -1:
            se[i], last = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
