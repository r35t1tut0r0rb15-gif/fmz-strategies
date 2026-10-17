"""RSI of the rate of change (HPotter), broker days: the RSI 20 of the 20-bar ROC above 70 holds a long, under 30 holds a
short (as written: strength is bought, weakness sold).
Port of FMZ strategy #431226 "基于ROC的RSI交易策略RSI-Based-on-ROC-Trading-Strategy" (RSI based on ROC).

FMZ source id: 431226

Source
    https://www.fmz.com/strategy/431226 (PineScript v2, FMZ last modified 2023-11-06 10:52:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-190), RSI 20 of ROC 20, BuyZone 30, SellZone 70
    nRes = rsi(roc(close, 20), 20);  nRes < 30 -> -1;  nRes > 70 -> 1;  else pos[1]
    pos == 1 -> entry long;  pos == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "BuyZone" opens shorts and the "SellZone" longs, as written. "Trade reverse" defaults to
      false and is fixed. RSI as Pine's (Wilder).
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels of a ROC.
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

NAME = "fmz_431226_rsi_of_roc_levels"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [20, 10],
    "roc_len": [20, 10],
}
DEFAULT_PARAMS = {"rsi_len": 20, "roc_len": 20, "buy_zone": 30, "sell_zone": 70}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    k = int(p["roc_len"])
    roc = 100 * (c - c.shift(k)) / c.shift(k)
    r = _rsi(roc.dropna(), int(p["rsi_len"])).reindex(c.index).to_numpy()
    m = len(r)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if r[i] < p["buy_zone"]:
            pos = -1
        elif r[i] > p["sell_zone"]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
