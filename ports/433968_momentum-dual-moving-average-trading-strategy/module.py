"""Noro's price channel with three entry kinds, 30-minute bars: in the channel's up trend two red bars above the centre, a
red close at the 30-bar channel low, or a fast RSI 2 under 25 above the centre go long; the mirrors go short; a sizeable
candle in the position's direction closes it.
Port of FMZ strategy #433968 "Momentum Dual Moving Average Trading Strategy" (Noro's Price Channel Strategy v1.2).

FMZ source id: 433968

Source
    https://www.fmz.com/strategy/433968 (PineScript v2, FMZ last modified 2023-12-01 18:13:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 176-239), price channel 30 (closes); trend / counter-trend / RSI entries on; longs and shorts on
    center = (highest(close, 30) + lowest(close, 30)) / 2;  trend = low > center ? 1 : high < center ? -1 : trend[1] (plot only)
    up1 = sma(bar, 2) == -1 and close > center;  up2 = close <= lowest(close, 30) and red;  up3 = rsi2 < 25 and close > center;  dn mirror
    up -> close a short, entry long;  dn -> close a long, entry short;  exit = (long and green or short and red) and body > sma(body, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel trend is computed but only plotted; the entries test the centre directly, as
      written. The fast RSI is rma-based on 2 bars.
    * Each bar from the position held at its start: a long is reversed by a short signal or closed by
      the exit (a further long signal is ignored, pyramiding 0); from flat a short signal wins over a
      long one (it is issued last). REVERSAL INTENDED. The lot is sizing. FREQ = "30min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel position, candle colours, RSI levels and body ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital % lot stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430009 (2 members, best partner #430009, Jaccard 0.726); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433968_noro_price_channel_v12"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pch": [30, 60],
    "rsi_limit": [25, 15],
}
DEFAULT_PARAMS = {"pch": 30, "rsi_limit": 25}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["pch"])
    hi, lo_ = c.rolling(n).max(), c.rolling(n).min()
    center = (hi + lo_) / 2
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=c.index).astype(float)
    sb = bar.rolling(2).mean()
    ch = c.diff()
    fu = ch.clip(lower=0).ewm(alpha=1 / 2, adjust=False).mean()
    fd = (-ch.clip(upper=0)).ewm(alpha=1 / 2, adjust=False).mean()
    fr = (100 - 100 / (1 + fu / fd)).where(fu != 0, 0.0).where(fd != 0, 100.0).where(fu.notna())
    body = (c - o).abs()
    big = (body > body.rolling(10).mean() / 2).to_numpy()
    lim = float(p["rsi_limit"])
    up = ((sb == -1) & (c > center) | (c <= lo_) & (c < o) | (fr < lim) & (c > center)).to_numpy()
    dn = ((sb == 1) & (c < center) | (c >= hi) & (c > o) | (fr > 100 - lim) & (c < center)).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        s = pos
        if s == 1:
            pos = -1 if dn[i] else (0 if (green[i] and big[i]) else 1)
        elif s == -1:
            pos = 1 if up[i] else (0 if (red[i] and big[i]) else -1)
        else:
            pos = -1 if dn[i] else (1 if up[i] else 0)
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
