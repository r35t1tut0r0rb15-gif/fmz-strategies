"""Noro's band scalper, broker days: a 20-bar close channel sets the trend (a close beyond the centre +- the average
distance with the bar's far side past the centre); in an up trend two red bars (or one large red body) go long and two
green bars closing above the fill price close the long; the mirror in a down trend goes short and covers.
Port of FMZ strategy #432340 "Trend Breakout Strategy Based on Bollinger Bands" (Noro's Bands Scalper Strategy v1.2).

FMZ source id: 432340

Source
    https://www.fmz.com/strategy/432340 (PineScript v2, FMZ last modified 2023-11-16 16:24:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 247-297), period 20, take 0 %, counter-trend entries off
    center = (highest(close, 20) + lowest(close, 20)) / 2; hd / ld = center +- sma(|close - center|, 20)
    trend = close < ld and high < center ? -1 : close > hd and low > center ? 1 : trend[1]
    up7 = trend 1 and (two red bars or (body > sma(body, 100) and red)) -> entry long
    dn7 = trend 1 and two green bars and close > avg price -> entry short with qty 0 (closes the long)
    dn8 = trend -1 and (two green bars or big green body) -> entry short;  up8 = trend -1, two red bars, close < avg price -> entry long qty 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * With counter-trend entries off, an entry against the trend gets quantity 0: it only closes the
      opposite position (Noro's idiom, as earlier ports). The avg-price tests use the fill price (the
      open after the entry signal); flat, they are false.
    * A trend-side entry while in the other side reverses: REVERSAL INTENDED. take % is 0. The band
      and background inputs only draw. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close channel, candle colours and body sizes against their own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the qty-0 entries stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: DG432340 (2 members, best partner #436249, Jaccard 0.823); ND426995 (4 members, best partner #430007, Jaccard 0.688); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432340_noro_band_scalper"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
}
DEFAULT_PARAMS = {"length": 20, "body_len": 100, "take_pct": 0.0}


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
    n = int(p["length"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    ds = (c - center).abs().rolling(n).mean()
    hd, ld = center + ds, center - ds
    t_dn = ((c < ld) & (h < center)).to_numpy()
    t_up = ((c > hd) & (lo > center)).to_numpy()
    body = (c - o).abs()
    big = (body > body.rolling(int(p["body_len"])).mean()).to_numpy()
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    red1 = np.concatenate(([False], red[:-1]))
    green1 = np.concatenate(([False], green[:-1]))
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tk = float(p["take_pct"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos, e_i = 0, 0, -1
    for i in range(m):
        if t_dn[i]:
            trend = -1
        elif t_up[i]:
            trend = 1
        start = pos
        ep = ov[e_i] if start != 0 else np.nan
        up7 = trend == 1 and ((red[i] and red1[i]) or (big[i] and red[i]))
        up8 = trend == -1 and red[i] and red1[i] and start != 0 and cv[i] < ep * (100 - tk) / 100
        dn7 = trend == 1 and green[i] and green1[i] and start != 0 and cv[i] > ep * (100 + tk) / 100
        dn8 = trend == -1 and ((green[i] and green1[i]) or (big[i] and green[i]))
        if up7 and start != 1:
            pos, e_i = 1, i + 1
        if up8 and start == -1:
            pos = 0
        if dn8 and start != -1:
            pos, e_i = -1, i + 1
        if dn7 and start == 1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
