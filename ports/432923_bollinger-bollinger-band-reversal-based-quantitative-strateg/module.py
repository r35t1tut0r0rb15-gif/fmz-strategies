"""Bollinger %B pull-back after a lagged washout, broker days, long only: when the close of three bars ago was below the
six closes around it with a wide band (width over 15 %, %B under 0.45, both on the close of three bars ago) between 7
and 57 bars back, and today's %B sits in 0.448-0.456, a long opens; an RSI 5 above 70 closes it.
Port of FMZ strategy #432923 "基于波动带反转的-Bollinger-量化策略Bollinger-Band-Reversal-Based-Quantitative-Strategy" (Bolinger strategy).

FMZ source id: 432923

Source
    https://www.fmz.com/strategy/432923 (PineScript v4, FMZ last modified 2023-11-22 17:44:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-182), RSI 5 (rma), BB length 20 with mult 20, bbw3 15, bbr3 0.45, bbr 0.448-0.456, since 7-57
    rsi = 100 - 100 / (1 + rma(up, 5) / rma(down, 5));  basis = sma(src, 20), dev = 20 stdev(src, 20); bbr, bbw (src = close or close[3])
    sincelowest = barssince(close[1..6] > close[3] and close > close[3] and bbw3 > 15 and bbr3 < 0.45)
    7 < sincelowest < 57 and 0.448 < bbr < 0.456 -> entry long;  rsi > 70 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band multiplier is 20 (not 2), as written: %B then stays close to 0.5 and the 0.448-0.456
      window is a narrow slice just under the basis. Pine's stdev is the population stdev.
    * barssince is undefined until the washout first happens (no entry before it). pyramiding is 1:
      a further entry while long is ignored; the RSI exit while flat does nothing.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band ratios, band width in percent and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() cash quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432923_bb_washout_pullback"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "since_max": [57, 30],
}
DEFAULT_PARAMS = {"length": 20, "mult": 20.0, "rsi_len": 5, "rsi_exit": 70.0, "bbw3_level": 15.0,
                  "bbr3_level": 0.45, "bbr_lower": 0.448, "bbr_higher": 0.456, "since_min": 7, "since_max": 57}


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


def _barssince(cond):
    v = cond.to_numpy()
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ch = c.diff()
    a = 1 / int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=a, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=a, adjust=False).mean()
    rsi = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn.replace(0.0, np.nan))))
    n, k = int(p["length"]), float(p["mult"])
    c3 = c.shift(3)
    b3 = c3.rolling(n).mean()
    d3 = k * c3.rolling(n).std(ddof=0)
    bbr3 = (c3 - (b3 - d3)) / (2 * d3)
    bbw3 = 2 * d3 / b3 * 100
    b = c.rolling(n).mean()
    d = k * c.rolling(n).std(ddof=0)
    bbr = (c - (b - d)) / (2 * d)
    wash = ((c.shift(6) > c3) & (c.shift(5) > c3) & (c.shift(4) > c3) & (c.shift(2) > c3) & (c.shift(1) > c3)
            & (c > c3) & (bbw3 > p["bbw3_level"]) & (bbr3 < p["bbr3_level"]))
    since = _barssince(wash)
    with np.errstate(invalid="ignore"):
        crit = ((since > int(p["since_min"])) & (since < int(p["since_max"]))
                & (bbr > p["bbr_lower"]).to_numpy() & (bbr < p["bbr_higher"]).to_numpy())
    ex = rsi > float(p["rsi_exit"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and crit[i]:
            pos = 1
        elif pos == 1 and ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
