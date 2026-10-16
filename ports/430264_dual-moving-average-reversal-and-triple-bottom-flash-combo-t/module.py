"""HPotter combo, broker days: the 2/20 EMA position and Bulkowski's three-day reversal pattern (previous day's state)
must agree; both long holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #430264 "Dual Moving Average Reversal and Triple Bottom Flash Combo Trading Strategy" (Combo 2/20 EMA & 3 Day Pattern).

FMZ source id: 430264

Source
    https://www.fmz.com/strategy/430264 (PineScript v4, FMZ last modified 2023-10-26 16:26:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 180-221), EMA 14; three-bar pattern read one day back through security("D", ..., lookahead_on)
    EMA20: xXA = ema(close, 14); nHH = max(high, high[1]); nLL = min(low, low[1])
           nXS = (nLL > xXA or nHH < xXA) ? nLL : nHH; pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    BarR:  open[2] > close[2] and high[1] < high[2] and low[1] < low[2] and low > low[1] and high > high[1] -> 1;
           mirror -> -1; else pos[1];  pos3BarR = security(ticker, "D", BarR[1], lookahead_on)
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the 1-day header chart, security("D", BarR[1], lookahead_on) is the chart's own pattern state
      one bar back (no future data: the [1] offset). The start-date inputs are unused (StartTrade =
      true). "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an EMA against two-bar extremes and a bar pattern.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430264_combo_ema20_three_day_pattern"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20, 30],
}
DEFAULT_PARAMS = {"length": 14}


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


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    hh = np.maximum(h, h.shift(1))
    ll = np.minimum(lo, lo.shift(1))
    xs = pd.Series(np.where((ll > xa) | (hh < xa), ll, hh), index=c.index)
    c1 = c.shift(1)
    pos1 = _hold((xs < c1).to_numpy(), (xs > c1).to_numpy())
    o2, c2, h1, h2, l1, l2 = o.shift(2), c.shift(2), h.shift(1), h.shift(2), lo.shift(1), lo.shift(2)
    bar_up = (o2 > c2) & (h1 < h2) & (l1 < l2) & (lo > l1) & (h > h1)
    bar_dn = (o2 < c2) & (h1 > h2) & (l1 > l2) & (h < h1) & (lo < l1)
    pos_bar = _hold(bar_up.to_numpy(), bar_dn.to_numpy())
    pos2 = np.concatenate(([0], pos_bar[:-1]))          # BarR[1]
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
