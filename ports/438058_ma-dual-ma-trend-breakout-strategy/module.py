"""Noro's Trend MAs v2.0 with CryptoBottom, 5-minute bars: in an uptrend of the 21-bar close channel centre, two red bars with the low under the 5-bar centre go long; so do a red bar with the high under both
centres, and a large red "crypto bottom" bar with a fast RSI under 10; in a downtrend, two green bars with the high over the 5-bar centre go short; reversing.
Port of FMZ strategy #438058 "双MA顺势突破策略Dual-MA-Trend-Breakout-Strategy" (Trend MAs str 2.0).

FMZ source id: 438058

Source
    https://www.fmz.com/strategy/438058 (PineScript v2, FMZ last modified 2024-01-08 16:43:38).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 182-263), long and short on; stops off (5 %); close source; fast MA filter on, fast 5, slow 21; bars 2; extreme on
    center = (highest(close, 21) + lowest(close, 21)) / 2, center2 the same over 5;  trend = 1 if low and low[1] above center, -1 if high and high[1] below it, else trend[1]
    up = trend 1 and low < center2 and two red bars;  up2 = high < center and high < center2 and a red bar;  up3 = red bar, |close - sma 10| > 3 x its 100-bar mean, min(open, close) < its previous value, fast RSI(2) < 10
    dn = trend -1 and high > center2 and two green bars;  up or up2 or up3 -> entry Long, exit(stop = stoplong);  dn -> entry Short, exit(stop = stopshort)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Stops are off, so the stop levels stay na and the exits place no order. dn2 is always 0. The fast
      RSI uses rma(2) of the gains and losses (down == 0 -> 100, up == 0 -> 0). trend starts na until a
      condition holds. strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity size is sizing.
      FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-channel centres, bar colours, a fast RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the unused stop percent stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427506 (4 members, best partner #440559, Jaccard 0.779); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438058_noro_trend_mas_cryptobottom"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slowlen": [21, 40],
    "fastlen": [5, 10],
}
DEFAULT_PARAMS = {"slowlen": 21, "fastlen": 5, "bars": 2, "needex": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sl, fl = int(p["slowlen"]), int(p["fastlen"])
    center = (c.rolling(sl).max() + c.rolling(sl).min()) / 2
    center2 = (c.rolling(fl).max() + c.rolling(fl).min()) / 2
    t_up = ((lo > center) & (lo.shift(1) > center.shift(1))).to_numpy()
    t_dn = ((h < center) & (h.shift(1) < center.shift(1))).to_numpy()
    m = len(c)
    trend = np.full(m, np.nan)
    for i in range(m):
        prev = trend[i - 1] if i > 0 else np.nan
        trend[i] = 1.0 if t_up[i] else (-1.0 if t_dn[i] else prev)
    bar = np.sign((c - o).to_numpy(dtype=float))
    nb = int(p["bars"])
    red = np.ones(m, dtype=bool)
    green = np.ones(m, dtype=bool)
    for k in range(nb):
        prev_bar = np.concatenate((np.full(k, np.nan), bar[:m - k])) if k else bar
        red &= prev_bar == -1
        green &= prev_bar == 1
    d = c.diff()
    fu, fd = _rma(d.clip(lower=0), 2), _rma((-d).clip(lower=0), 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        frsi = 100.0 - 100.0 / (1.0 + fu / fd)
    frsi = frsi.where(fu != 0, 0.0).where(fd != 0, 100.0)
    frsi = frsi.where(fd.notna() & (fu.notna() | (fd == 0))).to_numpy()
    dist = (c - c.rolling(10).mean()).abs()
    mn = np.minimum(o, c)
    up3 = ((c < o) & (dist > dist.rolling(100).mean() * 3) & (mn < mn.shift(1))).to_numpy() & (frsi < 10)
    cen2 = center2.to_numpy()
    up = (trend == 1) & (lo.to_numpy() < cen2) & red
    dn = (trend == -1) & (h.to_numpy() > cen2) & green
    up2 = ((h < center) & (h < center2)).to_numpy() & (bar == -1) & bool(p["needex"])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up | up2 | up3, index=ix), false, pd.Series(dn, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
