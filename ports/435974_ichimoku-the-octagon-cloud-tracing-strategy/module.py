"""Cloud and Tenkan trades, broker days: two rising candles over the displaced cloud, the bar over the Tenkan, go long (closed when a bar sits under the
Tenkan); two falling candles under the cloud, the bar under the Tenkan, go short (closed when a bar sits over the Tenkan).
Port of FMZ strategy #435974 "八角云霄-Ichimoku-趋势追踪策略The-Octagon-Cloud-Tracing-Strategy" (RENKO ICHIMOKU STRATEGY).

FMZ source id: 435974

Source
    https://www.fmz.com/strategy/435974 (PineScript v3, FMZ last modified 2023-12-20 15:08:22).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 161-216), Tenkan 10, Kijun 30, span B 60, displacement 30; "Renko" names are the open and close
    price_above_kumo = rc[1] > ro[1] and rc > ro and rc[1] > ss_high;  price_above_tenkan = open > tenkan and close > tenkan;  ss_high = max(spanA, spanB) 29 bars back
    entry long (above kumo and above tenkan), close long (below tenkan);  entry short (below kumo and below tenkan), close short (above tenkan)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ro / rc are the plain open and close (the script is not on Renko bricks). The cloud is read 29
      bars back (displacement - 1): past values only. The four orders of one bar are filled in the
      script's call order at the next open (entry long, close long, entry short, close short): a long
      entry on the bar of a short exit is a reversal. REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cloud and Tenkan rules.
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

NAME = "fmz_435974_cloud_tenkan_trades"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [10, 9],
    "kijun": [30, 26],
}
DEFAULT_PARAMS = {"tenkan": 10, "kijun": 30, "span_b": 60, "displacement": 30}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def donchian(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    tenkan, kijun = donchian(int(p["tenkan"])), donchian(int(p["kijun"]))
    span_a, span_b = (tenkan + kijun) / 2, donchian(int(p["span_b"]))
    k = int(p["displacement"]) - 1
    ss_high = np.maximum(span_a.shift(k), span_b.shift(k))
    ss_low = np.minimum(span_a.shift(k), span_b.shift(k))
    below_tenkan = (o < tenkan) & (c < tenkan)
    above_tenkan = (o > tenkan) & (c > tenkan)
    above_kumo = (c.shift(1) > o.shift(1)) & (c > o) & (c.shift(1) > ss_high)
    below_kumo = (c.shift(1) < o.shift(1)) & (c < o) & (c.shift(1) < ss_low)
    e_l = (above_kumo & above_tenkan).fillna(False).to_numpy()
    c_l = below_tenkan.fillna(False).to_numpy()
    e_s = (below_kumo & below_tenkan).fillna(False).to_numpy()
    c_s = above_tenkan.fillna(False).to_numpy()
    m = len(e_l)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            a, b, cc, d = pend
            if a and pos <= 0:
                pos = 1
            if b and pos == 1:
                pos = 0
            if cc and pos >= 0:
                pos = -1
            if d and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(e_l[i]), bool(c_l[i]), bool(e_s[i]), bool(c_s[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
