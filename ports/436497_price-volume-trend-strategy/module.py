"""Heikin-Ashi direction with a weak-move eliminator, broker days: while the smoothed Heikin-Ashi candle is up, a close that gains more than a price-unit threshold (on a non-doji candle) arms the buy state; the
mirror arms the sell state; each change of state (a first signal needs an earlier one) is a market entry, reversing.
Port of FMZ strategy #436497 "Price Volume Trend Strategy" (HA smoothed eliminator v2).

FMZ source id: 436497

Source
    https://www.fmz.com/strategy/436497 (PineScript v2, FMZ last modified 2023-12-25 13:09:48).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 122-247), HA length 1, strength toggle on (x 10000), strength elimination 600
    haclose = (o + h + l + c) / 4, haopen = (haopen[1] + haclose[1]) / 2 (first bar (o + c) / 2) on ema(price, 1);  uptrend = ema(haopen) < ema(haclose);  nRes = close - wma(close, 2) = (close - close[1]) / 3
    upcond = uptrend and nRes 10000 > 600;  dncond = downtrend and nRes 10000 < -600;  up = not uparrow[1] and upcond and candle not a doji;  dn mirror;  sig = 1 on up, -1 on dn, else sig[1]
    entry B when sig[1] != 1 and sig == 1;  entry S when sig[1] != -1 and sig == -1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The factor is a PRICE-UNIT threshold (a close-to-close gain over 0.18 price units); it is ported as
      written (an instrument with large prices passes it almost always). The candle-direction value is
      a number tested as a condition, so it only excludes doji candles. The comparison with the not yet
      set earlier state is false, so the first signal of a run cannot trade. The session backgrounds
      and the date window (true) place no orders. REVERSAL INTENDED. The percent-of-equity size is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, Heikin-Ashi state and a price-unit strength threshold.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_436497_ha_state_strength_eliminator"
FAMILY = "trend_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [600, 300],
    "len": [1, 2],
}
DEFAULT_PARAMS = {"factor": 600, "len": 1, "scale": 10000}


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
    n = int(p["len"])
    ema = lambda s: s.ewm(span=n, adjust=False).mean()      # noqa: E731
    op, hi, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o, h, l_, cc = ema(op), ema(hi), ema(lo), ema(c)
    haclose = ((o + h + l_ + cc) / 4).to_numpy()
    o_, c_ = o.to_numpy(), cc.to_numpy()
    m = len(haclose)
    haopen = np.empty(m)
    for i in range(m):
        haopen[i] = (o_[0] + c_[0]) / 2 if i == 0 else (haopen[i - 1] + haclose[i - 1]) / 2
    ho = pd.Series(haopen, index=bars_df.index)
    o2, c2 = ema(ho).to_numpy(), ema(pd.Series(haclose, index=bars_df.index)).to_numpy()
    is_up, is_dn = o2 < c2, o2 > c2
    strength = ((c - c.shift(1)) / 3 * float(p["scale"])).to_numpy()
    fac = float(p["factor"])
    with np.errstate(invalid="ignore"):
        upc = is_up & (strength > fac)
        dnc = is_dn & (strength < -fac)
    candle = (op.to_numpy() != c.to_numpy())
    ua = da = False
    sg = np.full(m, np.nan)
    prev_sg = np.nan
    buy = np.zeros(m, dtype=bool)
    sell = np.zeros(m, dtype=bool)
    for i in range(m):
        ua_prev, da_prev = ua, da
        ua = False if is_dn[i] else (True if ua_prev else bool(upc[i]))
        da = False if is_up[i] else (True if da_prev else bool(dnc[i]))
        up = (not ua_prev) and bool(upc[i]) and bool(candle[i])
        dn = (not da_prev) and bool(dnc[i]) and bool(candle[i])
        cur = 1.0 if up else (-1.0 if dn else prev_sg)
        if not np.isnan(prev_sg):
            buy[i] = cur == 1.0 and prev_sg != 1.0
            sell[i] = cur == -1.0 and prev_sg != -1.0
        sg[i] = cur
        prev_sg = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
