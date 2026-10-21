"""Darvas box breakouts with a MavilimW filter and a box stop, broker days: a close crossing over the box top while above the MavilimW average goes long (from flat), a close crossing under the box bottom while below it
goes short; the stop sits at the opposite box edge; a profitable trade also closes when the relative vigor index crosses its signal line against it.
Port of FMZ strategy #436757 "Trending Darvas Box Quantitative Trading Strategy" (TradeIQ Darvas Box Test).

FMZ source id: 436757

Source
    https://www.fmz.com/strategy/436757 (PineScript v5, FMZ last modified 2023-12-27 14:45:41).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 133-204), box length 5, MavilimW 3 / 5, RVI length 10
    NH = valuewhen(high > highest(high, 5)[1], high, 0);  TopBox / BottomBox = valuewhen(barssince(high > k1[1]) == 3 and highest(high, 3) < highest(high, 4), NH / lowest(low, 5), 0);  MAVW = wma chain 3, 5, 8, 13, 21, 34
    long = crossover(close, TopBox) and close > MAVW -> entry when flat, exit(stop = BottomBox) set once;  close when open profit > 0 and crossunder(rvi, sig);  short mirror (crossunder BottomBox, stop TopBox, crossover(rvi, sig))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The box is followed bar by bar with valuewhen / barssince as written. The stop is the opposite box
      edge as a distance from the signal close (TopBox - close or close - BottomBox, over the close),
      shifted one bar inside stops() and re-based on the fill; the script sets it at the close of the fill
      bar from that bar's box, which differs only when a new box completes on the fill bar. "Flat" and
      the open profit follow the house bracket: the loop marks the position closed once a bar's low /
      high reaches the stop (from the fill price) or the RVI rule closes it, and the open profit is the
      close against the fill price. The trade cap (closedtrades < 100) is a backtest limit and the date
      window is true: both dropped. Opposite entries cannot occur (entries from flat). Stop module:
      portfolio_kwargs {} (driver D4). The 100 % of equity size is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, box levels as distances from the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436757_darvas_box_mavilimw_stop"
FAMILY = "breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "boxp": [5, 8],
    "rvi_len": [10, 14],
}
DEFAULT_PARAMS = {"boxp": 5, "rvi_len": 10, "fmal": 3, "smal": 5}


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


def _swma(x):
    return (x + 2.0 * x.shift(1) + 2.0 * x.shift(2) + x.shift(3)) / 6.0


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["boxp"])
    ll = lo.rolling(n).min().to_numpy()
    k1 = h.rolling(n).max()
    newhigh = (h > k1.shift(1)).to_numpy()
    box1 = (h.rolling(n - 2).max() < h.rolling(n - 1).max()).to_numpy()
    hv = h.to_numpy(dtype=float)
    m = len(hv)
    top, bot = np.full(m, np.nan), np.full(m, np.nan)
    nh, since, t_, b_ = np.nan, None, np.nan, np.nan
    for i in range(m):
        if newhigh[i]:
            nh, since = hv[i], 0
        elif since is not None:
            since += 1
        if since == n - 2 and box1[i]:
            t_, b_ = nh, ll[i]
        top[i], bot[i] = t_, b_
    top_s, bot_s = pd.Series(top, index=c.index), pd.Series(bot, index=c.index)
    fm, sm = int(p["fmal"]), int(p["smal"])
    tm = fm + sm
    fm2 = sm + tm
    ftm = tm + fm2
    sm2 = fm2 + ftm
    mavw = c
    for k in (fm, sm, tm, fm2, ftm, sm2):
        mavw = _wma(mavw, k)
    ln = int(p["rvi_len"])
    with np.errstate(divide="ignore", invalid="ignore"):
        rvi = _swma(c - o).rolling(ln).sum() / _swma(h - lo).rolling(ln).sum()
    sig = _swma(rvi)
    long_c = (c > top_s) & (c.shift(1) <= top_s.shift(1)) & (c > mavw)
    short_c = (c < bot_s) & (c.shift(1) >= bot_s.shift(1)) & (c < mavw)
    rvi_dn = (rvi < sig) & (rvi.shift(1) >= sig.shift(1))
    rvi_up = (rvi > sig) & (rvi.shift(1) <= sig.shift(1))
    f_l = (c - bot_s) / c
    f_s = (top_s - c) / c
    f = pd.Series(np.where(long_c, f_l, np.where(short_c, f_s, np.nan)), index=c.index)
    f = f.where(f > 0)
    return long_c, short_c, rvi_dn, rvi_up, f


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    enter_l, enter_s, exit_l, exit_s, f = _setup(bars_df, p)
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    el, es, xl, xs, fv = (enter_l.to_numpy(), enter_s.to_numpy(), exit_l.to_numpy(), exit_s.to_numpy(),
                          f.to_numpy())
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, sl_f = 0, -1, np.nan
    pend_exit = False
    for i in range(m):
        if pend_exit and pos != 0:                       # the close fills at this bar's open
            pos = 0
        pend_exit = False
        if pos != 0 and i >= entry_i:                    # house stop from the fill price
            e = ov[entry_i]
            if pos == 1 and lv[i] <= e * (1 - sl_f):
                pos = 0
            elif pos == -1 and hv[i] >= e * (1 + sl_f):
                pos = 0
        if pos != 0 and i >= entry_i:
            e = ov[entry_i]
            if pos == 1 and xl[i] and cv[i] > e:
                lx[i] = True
                pend_exit = True
            elif pos == -1 and xs[i] and cv[i] < e:
                sx[i] = True
                pend_exit = True
        elif pos == 0 and i + 1 < m and not np.isnan(fv[i]):
            if el[i]:
                le[i] = True
                pos, entry_i, sl_f = 1, i + 1, fv[i]
            elif es[i]:
                se[i] = True
                pos, entry_i, sl_f = -1, i + 1, fv[i]
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = _setup(bars_df, p)[4]
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
