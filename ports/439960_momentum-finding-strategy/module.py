"""Noro's squeeze momentum, mode 2, 30-minute bars: with the linear-regression momentum (20) above zero but falling, the script goes long; below zero but rising, short; a long closing above its entry price
or a short below it is closed; reversing.
Port of FMZ strategy #439960 "Momentum Finding Strategy" (Noro's Squeeze Momentum Strategy v1.1).

FMZ source id: 439960

Source
    https://www.fmz.com/strategy/439960 (PineScript v2, FMZ last modified 2024-01-25 12:34:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-239), long and short on; leverage 1; BB 20 x 2 (the code uses the KC factor 1.5), KC 20 x 1.5; mode 2 on; candle colour and EMA body on (mode 1 only); date inputs unused
    val = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0);  trend = sign(val)
    up2 = trend == 1 and val < val[1];  dn2 = trend == -1 and val > val[1];  exit = (long and close > avg price) or (short and close < avg price) and mode2;  entries, then close_all on exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * Mode 2 is on, so the mode-1 colour and body tests are off; the squeeze states only colour the plot.
      The exit reads Pine's precedence (the "and mode2" binds to the short test; mode 2 is on, so both
      apply). The average price is the fill open. The final close_all acts on the position held at the
      bar close and the bar ends flat (as #430380); from flat the exit cannot fire and the signal opens.
      REVERSAL INTENDED. The equity lot is sizing. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression momentum and an entry-price test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity lot and leverage stored.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND436540 (2 members, best partner #436540, Jaccard 0.667); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439960_noro_squeeze_momentum_mode2"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_kc": [20, 30, 14],
}
DEFAULT_PARAMS = {"length_kc": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(y, n):
    """Pine's linreg(y, n, 0): the least-squares line over the last n bars, read at the newest bar."""
    k = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sky = (k * y).rolling(n).sum()
    x0 = k - (n - 1)                                   # x = k - x0 runs 0 .. n-1 inside the window
    sxy = sky - x0 * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length_kc"])
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    val = _linreg(c - mid, n)
    vv = val.to_numpy()
    vp = val.shift(1).to_numpy()
    with np.errstate(invalid="ignore"):
        up = (vv > 0) & (vv < vp)
        dn = (vv < 0) & (vv > vp)
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, ep = 0, np.nan
    for i in range(m):
        ex = (pos == 1 and cv[i] > ep) or (pos == -1 and cv[i] < ep)
        new = pos
        if up[i] and pos != 1:
            new = 1
        elif dn[i] and pos != -1:
            new = -1
        if ex:
            new = 0
        if new != pos and new != 0:
            ep = ov[i + 1] if i + 1 < m else np.nan
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
