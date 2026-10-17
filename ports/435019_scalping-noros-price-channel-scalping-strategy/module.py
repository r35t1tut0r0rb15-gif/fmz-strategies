"""Noro's Bands Scalper v1.0, 3-hour bars: a price-channel trend (close beyond the centre +- its mean distance with the bar
inside the opposite band) sets the side. In an up-trend two red bars go long and two green bars with the close above the
entry price close the long; in a down-trend two green bars go short and two red bars with the close below the entry
price close the short.
Port of FMZ strategy #435019 "诺罗波动通道scalping策略Noros-Price-Channel-Scalping-Strategy" (Noro's Bands Scalper Strategy v1.0).

FMZ source id: 435019

Source
    https://www.fmz.com/strategy/435019 (PineScript v2, FMZ last modified 2023-12-11 17:06:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 110-157), period 20 on close; long and short on
    center = (highest(close, 20) + lowest(close, 20)) / 2;  d = sma(|close - center|, 20);  hd / ld = center +- d
    trend = close < ld and high < hd ? -1 : close > hd and low > ld ? 1 : trend[1]
    up7 = trend 1 and two red bars -> entry long;  dn7 = trend 1 and two green bars and close > avg price -> entry short, qty 0
    up8 = trend -1 and two red bars and close < avg price -> entry long, qty 0;  dn8 = trend -1 and two green bars -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * An entry against the trend has qty 0: it only closes the opposite position (Noro's idiom; as
      #430007 and worker A's #426995). The average price is the position's fill (the next open after
      the signal); with no position it is na and the closing tests are false.
    * strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity is sizing. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts against a channel trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND426995 (4 members, best partner #426995, Jaccard 0.744); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435019_noro_bands_scalper_v10"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10],
}
DEFAULT_PARAMS = {"length": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    d = (c - center).abs().rolling(n).mean()
    hd, ld = (center + d).to_numpy(), (center - d).to_numpy()
    bar = np.sign(c - o).to_numpy()
    bar1 = np.concatenate(([0.0], bar[:-1]))
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    trend, pos, avg, pending = 0, 0, np.nan, False
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pending:                                  # the entry fills at this bar's open
                avg, pending = ov[i], False
            if cv[i] < ld[i] and hv[i] < hd[i]:
                trend = -1
            elif cv[i] > hd[i] and lv[i] > ld[i]:
                trend = 1
            red2, green2 = bar[i] == -1 and bar1[i] == -1, bar[i] == 1 and bar1[i] == 1
            up7 = trend == 1 and red2
            dn8 = trend == -1 and green2
            dn7 = trend == 1 and green2 and pos == 1 and cv[i] > avg
            up8 = trend == -1 and red2 and pos == -1 and cv[i] < avg
            if pos == 0:
                new = 1 if up7 else (-1 if dn8 else 0)
            elif pos == 1:
                new = -1 if dn8 else (0 if dn7 else 1)
            else:
                new = 1 if up7 else (0 if up8 else -1)
            if new != pos:
                le[i], se[i] = new == 1, new == -1
                lx[i], sx[i] = pos == 1 and new == 0, pos == -1 and new == 0
                pending = new != 0
                avg = np.nan if new == 0 else avg
                pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
