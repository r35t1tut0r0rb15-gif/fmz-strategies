"""Regression SSL channel shorts under a DEMA average, short only, 1-hour bars: the SSL lines (linreg of highs and lows, 89) crossing down with the 200-bar average of the DEMA 200 above the close goes short;
the SSL lines crossing up or the close crossing over that average closes.
Port of FMZ strategy #440066 "Linear Regression and Dual Moving Average Short Term Strategy" (LR&SSL_Short).

FMZ source id: 440066

Source
    https://www.fmz.com/strategy/440066 (PineScript v4, FMZ last modified 2024-01-26 12:33:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-181), period 89; DEMA 200; start 2017-12-17 (open)
    smaHigh = linreg(high, 89, 0);  smaLow = linreg(low, 89, -1);  Hlv = close > smaHigh ? 1 : close < smaLow ? -1 : previous;  sslDown / sslUp by Hlv
    dema = sma(2 ema200 - ema(ema200, 200), 200);  entry short on crossunder(sslUp, sslDown) and dema > close;  close short on crossover(sslUp, sslDown) or crossover(close, dema)

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg with offset -1 reads the window's line one bar beyond its newest bar (data up to the
      current bar only). The entry and the close cannot share a bar. Short only. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression channel crossings and a smoothed DEMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440066_lr_ssl_dema_short"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [89, 50],
    "length": [200, 100],
}
DEFAULT_PARAMS = {"len": 89, "length": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(y, n, offset=0):
    """Pine's linreg(y, n, offset): the least-squares line over the last n bars, read at n - 1 - offset."""
    k = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sky = (k * y).rolling(n).sum()
    x0 = k - (n - 1)                                   # x = k - x0 runs 0 .. n-1 inside the window
    sxy = sky - x0 * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1 - offset)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len"])
    sh = _linreg(h, n, 0).to_numpy()
    sl = _linreg(lo, n, -1).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    hlv = np.full(m, np.nan)
    for i in range(m):
        prev = hlv[i - 1] if i > 0 else np.nan
        hlv[i] = 1 if cv[i] > sh[i] else (-1 if cv[i] < sl[i] else prev)
    neg = hlv < 0
    s_dn = pd.Series(np.where(neg, sh, sl), index=c.index)
    s_up = pd.Series(np.where(neg, sl, sh), index=c.index)
    L = int(p["length"])
    d1 = c.ewm(span=L, adjust=False).mean()
    d2 = 2 * d1 - d1.ewm(span=L, adjust=False).mean()
    dema = d2.rolling(L).mean()
    xu = (s_up < s_dn) & (s_up.shift(1) >= s_dn.shift(1))
    xo = (s_up > s_dn) & (s_up.shift(1) <= s_dn.shift(1))
    se = xu & (dema > c)
    sx = xo | ((c > dema) & (c.shift(1) <= dema.shift(1)))
    false = pd.Series(False, index=c.index)
    return false, false.copy(), se, sx


def portfolio_kwargs(**params):
    return {}
