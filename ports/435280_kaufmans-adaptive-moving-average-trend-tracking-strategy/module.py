"""Kaufman adaptive average trend, broker days: the close above the KAMA (of hl2) goes long, below it goes short (reversing);
the "Crossing" type uses the slope of the KAMA instead. The KAMA starts from zero, as written.
Port of FMZ strategy #435280 "Kaufmans Adaptive Moving Average Trend Tracking Strategy" (Noro's KAMA Strategy).

FMZ source id: 435280

Source
    https://www.fmz.com/strategy/435280 (PineScript v3, FMZ last modified 2023-12-13 17:25:33).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 155-180), length 3, fast 2, slow 30; type Trend; long and short on
    er = |src[1] - src[length]| / sum(|src - src[1]|, length);  sc = (er (2/(fast+1) - 2/(slow+1)) + 2/(slow+1))^2;  kama = nz(kama[1]) + sc (hl2 - nz(kama[1]))
    Trend: up = close > kama, dn = close < kama;  Crossing: up = kama > kama[1], dn = kama < kama[1];  up -> entry long;  dn -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recursion starts from nz(kama[1]) = 0 at the first valid bar, so the average climbs to the
      price slowly (sc is a few per cent): the early trades in a series are that start-up, as written.
      The efficiency ratio's numerator uses src[1] and src[length], as written. strategy.entry
      reverses: REVERSAL INTENDED. The date window is the 1900-2100 default (always true). The
      equity-based lot is sizing. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot and pyramiding input stored.
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

NAME = "fmz_435280_kama_trend_follow"
FAMILY = "adaptive_average"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 10],
    "type": ["Trend", "Crossing"],
}
DEFAULT_PARAMS = {"length": 3, "fast": 2, "slow": 30, "type": "Trend"}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    vol = c.diff().abs().rolling(n).sum()
    chg = (c.shift(1) - c.shift(n)).abs()
    with np.errstate(invalid="ignore", divide="ignore"):
        er = (chg / vol).where(vol != 0, 0.0)
    fsc, ssc = 2 / (int(p["fast"]) + 1), 2 / (int(p["slow"]) + 1)
    sc = ((er * (fsc - ssc) + ssc) ** 2).to_numpy()
    bid = ((h + lo) / 2).to_numpy(dtype=float)
    m = len(bid)
    kama = np.full(m, np.nan)
    for i in range(m):
        prev = kama[i - 1] if i > 0 and not np.isnan(kama[i - 1]) else 0.0   # nz(kama[1])
        kama[i] = prev + sc[i] * (bid[i] - prev)                              # NaN when sc or hl2 is missing
    k = pd.Series(kama, index=c.index)
    if p["type"] == "Crossing":
        up, dn = k > k.shift(1), k < k.shift(1)
    else:
        up, dn = c > k, c < k
    upv, dnv = up.to_numpy(), dn.to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if upv[i]:
            q = 1
        elif dnv[i]:
            q = -1
        tgt[i] = q
    prv = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prv != 1), index=ix), false,
            pd.Series((tgt == -1) & (prv != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
