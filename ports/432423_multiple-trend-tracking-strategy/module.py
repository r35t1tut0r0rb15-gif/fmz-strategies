"""MACD histogram and RSI crosses, broker days: the MACD histogram (12 / 26 / 9) crossing above zero or the RSI 18 crossing
above 30 goes long; the histogram crossing below zero or the RSI 18 crossing under 70 goes short; always in once started.
The ATR trend line and the DEMA only draw.
Port of FMZ strategy #432423 "Multiple Trend Tracking Strategy" (Atrend by OTS).

FMZ source id: 432423

Source
    https://www.fmz.com/strategy/432423 (PineScript v4, FMZ last modified 2023-11-17 17:19:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 184-206), MACD 12 / 26 / 9, RSI 18 with 30 / 70
    crossover(delta, 0) -> entry long ("MACD buy");  crossunder(delta, 0) -> entry short ("MACD sell")
    crossover(rsi18, 30) -> entry long ("RSI buy");  crossunder(rsi18, 70) -> entry short ("RSI sell")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four entries share two directions (pyramiding 0): a same-side entry while in that side adds
      nothing, an opposite one reverses; on a bar with signals both ways the later statement in the
      source wins (RSI after MACD, sell after buy). The SuperTrend-style trend, its alerts and the
      DEMA place no order. REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram and RSI crosses.
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

NAME = "fmz_432423_macd_rsi_cross_flip"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [18, 14],
    "fast": [12, 8],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "rsi_len": 18, "os": 30, "ob": 70}


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


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    os_, ob = float(p["os"]), float(p["ob"])
    m_up = ((delta > 0) & (delta.shift(1) <= 0)).to_numpy()
    m_dn = ((delta < 0) & (delta.shift(1) >= 0)).to_numpy()
    r_up = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    r_dn = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        for sig, side in ((m_up[i], 1), (m_dn[i], -1), (r_up[i], 1), (r_dn[i], -1)):
            if sig:
                pos = side
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
