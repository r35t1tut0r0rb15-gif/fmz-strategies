"""Noro's Bands Scalper v1.6: a price-channel trend (close beyond the centre +- its mean distance,
the bar fully on one side of the centre) sets the side. In an up-trend two red bars, or a red bar
with a large body, go long, and two green bars or a close above the upper band, with the close above
the entry price, close the long; in a down-trend the mirror (green bars short; red bars or a close
under the lower double band, below the entry price, close the short).
Port of FMZ strategy #427185 "Momentum Breakout Trading Strategy".

FMZ source id: 427185

Source
    https://www.fmz.com/strategy/427185 (PineScript v2, FMZ last modified 2023-09-18 21:28:22).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 150-221), period 20, take 0 %, bands entry on,
counter-trend off, body length 10, trend bars 1
    center = (highest(close, 20) + lowest(close, 20)) / 2; d = sma(|close - center|, 20)
    hd / ld = center +- d; ld2 = center - 2 d
    trend = close < ld and high < center ? -1 : close > hd and low > center ? 1 : trend[1]
    smabody = ema(|close - open|, 30) / 10 x bodylen
    up7 = trend 1 and (two red bars or (body > smabody and red))              -> entry long
    dn7 = trend 1 and (two green bars or close > hd) and close > avg price     -> entry short, qty 0
    up8 = trend -1 and (two red bars or close < ld2) and close < avg price     -> entry long, qty 0
    dn8 = trend -1 and (two green bars or (body > smabody and green))          -> entry short

Interpretation choices (Pine rules in SURVEY_README.md; as worker A's #426995)
    * Counter-trend entries are off, so an entry against the trend has qty 0: it only closes the
      opposite position (Noro's idiom). The average price is the position's fill (the next open
      after the signal); with no position it is na and the closing tests are false.
    * strategy.entry reverses: REVERSAL INTENDED. The year / month window (1900-2100) is the
      author's backtest window: dropped.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts, ratios of averages, a percent take of 0.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per trade stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: DG427185 (2 members, with #439225, Jaccard 0.858); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427185_noro_bands_scalper_v16"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
    "bodylen": [10, 15],
}
DEFAULT_PARAMS = {"length": 20, "bodylen": 10, "takepercent": 0.0, "trb": 1, "needbe": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, trb = int(p["length"]), int(p["trb"])
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    d = (c - center).abs().rolling(n).mean()
    hd, ld, ld2 = center + d, center - d, center - 2 * d
    chd, cld = c > hd, c < ld
    up_t, dn_t = chd.copy(), cld.copy()
    for k in range(1, trb):
        up_t &= chd.shift(k, fill_value=False)
        dn_t &= cld.shift(k, fill_value=False)
    body = (c - o).abs()
    smabody = body.ewm(span=30, adjust=False).mean() / 10 * p["bodylen"]
    bar = np.sign(c - o).to_numpy()
    bar1 = np.concatenate(([0.0], bar[:-1]))
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    cen, hdv, ld2v = center.to_numpy(), hd.to_numpy(), ld2.to_numpy()
    upt, dnt = up_t.to_numpy(), dn_t.to_numpy()
    bigb = (body > smabody).to_numpy()
    needbe, take = bool(p["needbe"]), float(p["takepercent"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos, avg, pending = 0, 0, np.nan, False
    for i in range(m):
        if pending:                                  # the entry fills at this bar's open
            avg, pending = ov[i], False
        if dnt[i] and hv[i] < cen[i]:
            trend = -1
        elif upt[i] and lv[i] > cen[i]:
            trend = 1
        red2, green2 = bar[i] == -1 and bar1[i] == -1, bar[i] == 1 and bar1[i] == 1
        up7 = trend == 1 and (red2 or (bigb[i] and bar[i] == -1))
        dn8 = trend == -1 and (green2 or (bigb[i] and bar[i] == 1))
        dn7 = (trend == 1 and (green2 or (cv[i] > hdv[i] and needbe)) and pos == 1
               and cv[i] > avg * (100 + take) / 100)
        up8 = (trend == -1 and (red2 or (cv[i] < ld2v[i] and needbe)) and pos == -1
               and cv[i] < avg * (100 - take) / 100)
        new = pos
        if pos == 0:
            new = 1 if up7 else (-1 if dn8 else 0)
        elif pos == 1:
            new = -1 if dn8 else (0 if dn7 else 1)
        else:
            new = 1 if up7 else (0 if up8 else -1)
        if new != pos:
            pending = new != 0
            avg = np.nan if new == 0 else avg
            pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
