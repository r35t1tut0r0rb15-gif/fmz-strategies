"""DI crossings with a Hull filter, net-order effect, broker days: a DI+ crossing over DI- (76-bar Wilder sums) with the HMA 29 above the HMA 2 buys one unit (opening a long from flat, flattening a short); the
mirror sells one unit; positions are never reversed in one step.
Port of FMZ strategy #437675 "动向指标与-Hull-平均线组合策略DMI-and-HMA-Combination-Strategy" (DMI + HMA - No Risk Management).

FMZ source id: 437675

Source
    https://www.fmz.com/strategy/437675 (PineScript v4, FMZ last modified 2024-01-04 17:23:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 127-165), Hull 29 / 2, DI length 76; pyramiding 1
    SmoothedTR / DM+ / DM- = nz(prev) - nz(prev) / 76 + current;  DI+ / DI- = 100 x DM / TR;  go_long = crossover(DI+, DI-) and hma 29 > hma 2;  go_short mirror
    flat or short -> strategy.order("long", long, when go_long);  flat or long -> strategy.order("Short", short, when go_short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order adds its quantity to the position (not a reversing entry); with the same 100 % size
      each time, a buy while short brings the position to flat and a buy while flat opens a long
      (SURVEY_README: strategy.order by its net effect); pyramiding 1 blocks a second same-side unit. The
      DI sums seed at 0 (nz) as written. The hma is Pine's built-in (integer n / 2, rounded sqrt).
      Opposite entries cannot occur (each order moves one step). The 100 % of equity size and commission
      are sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, directional indicators and Hull averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, pyramiding and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437675_di_cross_hull_net_order"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hull_len1": [29, 15],
    "di_len": [76, 30],
}
DEFAULT_PARAMS = {"hull_len1": 29, "hull_len2": 2, "di_len": 76}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def _wsum(x, n):
    v = x.to_numpy(dtype=float)
    out = np.zeros(len(v))
    prev = 0.0
    for i in range(len(v)):
        out[i] = prev - prev / n + v[i]
        prev = 0.0 if np.isnan(out[i]) else out[i]
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1).fillna(0.0)
    h1, l1 = h.shift(1).fillna(0.0), lo.shift(1).fillna(0.0)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    dmp = pd.Series(np.where(h - h1 > l1 - lo, np.maximum(h - h1, 0), 0.0), index=c.index)
    dmm = pd.Series(np.where(l1 - lo > h - h1, np.maximum(l1 - lo, 0), 0.0), index=c.index)
    n = int(p["di_len"])
    s_tr, s_p, s_m = _wsum(tr, n), _wsum(dmp, n), _wsum(dmm, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        dip, dim = s_p / s_tr * 100, s_m / s_tr * 100
    fh, sh = _hma(c, int(p["hull_len1"])), _hma(c, int(p["hull_len2"]))
    gl = ((dip > dim) & (dip.shift(1) <= dim.shift(1)) & (fh > sh)).to_numpy()
    gs = ((dim > dip) & (dim.shift(1) <= dip.shift(1)) & (fh < sh)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s = pos
        if gl[i] and pos <= 0:
            s = pos + 1
        if gs[i] and pos >= 0:
            s = s - 1
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        elif s == 0 and pos == 1:
            lx[i] = True
        elif s == 0 and pos == -1:
            sx[i] = True
        pos = s
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
