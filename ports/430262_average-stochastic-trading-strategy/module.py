"""Averaged stochastic, broker days: the EMA-smoothed average of stochastic K and D (21 / 3 / 3) crossing above its EMA
signal under 20 goes long, crossing below it over 80 goes short; the signal line above 80 closes a long, under 20
closes a short. Adds are not ported.
Port of FMZ strategy #430262 "Average Stochastic Trading Strategy" (AVG Stochastic Strategy [M30 Backtesting]).

FMZ source id: 430262

Source
    https://www.fmz.com/strategy/430262 (PineScript v5, FMZ last modified 2023-10-26 16:20:33).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-222), %K 21, smoothing 3 / 3, levels 20 / 80, pyramiding 3
    k = sma(stoch(close, high, low, 21), 3); d = sma(k, 3)
    avg_k = ema((k + d) / 2, 3); avg_d = ema(avg_k, 3)
    up = avg_k crosses above avg_d and avg_d < 20 -> entry long;  dn = crosses below and avg_d > 80 -> entry short
    avg_d > 80 -> close long;  avg_d < 20 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 3: a further same-side signal adds in the source; adds are not ported.
    * An entry signal implies the other side's close (up needs avg_d < 20): the bar reverses. A close
      acts on the position held at the start of the bar.
    * The header period (1d) is used; the comment's M30 is the author's suggestion. strategy.entry
      reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D".

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 3 stored in original_sizing.txt.
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

NAME = "fmz_430262_avg_stochastic"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_k": [21, 14],
    "smooth_k": [3, 5],
}
DEFAULT_PARAMS = {"period_k": 21, "smooth_k": 3, "period_d": 3, "low": 20, "high": 80}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, sk, pd_ = int(p["period_k"]), int(p["smooth_k"]), int(p["period_d"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(sk).mean()
    d = k.rolling(pd_).mean()
    ak = ((k + d) / 2).ewm(span=sk, adjust=False).mean()
    ad = ak.ewm(span=pd_, adjust=False).mean()
    up = ((ak.shift(1) < ad.shift(1)) & (ak > ad) & (ad < p["low"])).to_numpy()
    dn = ((ak.shift(1) > ad.shift(1)) & (ak < ad) & (ad > p["high"])).to_numpy()
    xl = (ad > p["high"]).to_numpy()
    xs = (ad < p["low"]).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        elif pos == 1 and xl[i]:
            pos = 0
        elif pos == -1 and xs[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
