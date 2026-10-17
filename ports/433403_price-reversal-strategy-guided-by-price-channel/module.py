"""Noro's price-channel pull-backs, 1-minute bars: the trend turns up when the low is above the middle of the 30-bar close
channel and down when the high is below it; in an up trend a red candle with a body above a fifth of the 10-bar average
body goes long, in a down trend a green one goes short. Always in after the first signal.
Port of FMZ strategy #433403 "Price Reversal Strategy Guided by Price Channel" (Noro's PriceChannel for D1 v1.0).

FMZ source id: 433403

Source
    https://www.fmz.com/strategy/433403 (PineScript v2, FMZ last modified 2023-11-27 11:40:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 142-191), price channel 30 (closes), pc bars 1; colour and body filters on
    center = (highest(close, 30) + lowest(close, 30)) / 2;  trend = sma(low > center, 1) == 1 ? 1 : sma(high < center, 1) == 1 ? -1 : trend[1]
    up = trend == 1 and close < open and body > sma(body, 10) / 5 -> entry long;  dn = trend == -1 and close > open and the same body test -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel is of closes and includes the current bar, as written. The title's "D1" is not the
      header's period: FREQ = "1min" from the backtest header (the source was tested on 1-minute bars).
    * strategy.entry reverses: REVERSAL INTENDED. The date window is open. The background colour is a
      plot only.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel position, candle colour and body ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433403_noro_price_channel_pullback"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slowlen": [30, 60],
    "pcbars": [1, 3],
}
DEFAULT_PARAMS = {"slowlen": 30, "pcbars": 1}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["slowlen"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    pb = int(p["pcbars"])
    ub = (lo > center).astype(float).rolling(pb).mean().to_numpy()
    db = (h < center).astype(float).rolling(pb).mean().to_numpy()
    body = (c - o).abs()
    big = (body > body.rolling(10).mean() / 5).to_numpy()
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos = 0, 0
    for i in range(m):
        if ub[i] == 1:
            trend = 1
        elif db[i] == 1:
            trend = -1
        if trend == 1 and red[i] and big[i]:
            pos = 1
        elif trend == -1 and green[i] and big[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
