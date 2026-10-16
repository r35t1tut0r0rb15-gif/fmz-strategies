"""BTC long trend, hourly bars, long only: with ATR(14) under 2 % of the price, SMA 200 rising over 10
bars, the MACD line, EMA 20 and SMA 100 rising and EMA 20 above SMA 100 below the close, go long; close
on a 1.5 % close-checked stop from the signal close or when EMA 20 crosses under SMA 100 (previous bar).
Port of FMZ strategy #428579 "BTC and ETH Long Trend Strategy" (BTC Long strategy).

FMZ source id: 428579

Source
    https://www.fmz.com/strategy/428579 (PineScript v4, FMZ last modified 2023-10-07 10:16:09).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 171-307), MACD 12/26/7, EMA 20, SMA 100 / 200, ATR 14, stop 1.5 %
    entry (not opened): atr / close x 100 < 2 and rising(sma200, 10) and rising(macd, 3) and rising(ema20, 2)
        and rising(sma100, 3) and ema20 > sma100 and sma100 < close; stop = close x (1 - 1.5 %)
    close (opened): close <= stop or crossunder(ema20[1], sma100[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, n) = x above every one of its previous n values (Pine). The flags carry over through
      [1] (as var). The stop is checked on the close (an exit signal, filled at the next open);
      the same-bar check after an entry is as written.
    * The fixed USD position size and leverage are sizing. Long only.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths, volatility percentage, percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: position size and leverage stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND428579 (2 members, best partner #439200, Jaccard 0.733); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428579_btc_long_trend_filters"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_loss": [1.5, 3.0],
    "vol_max": [2.0, 3.0],
}
DEFAULT_PARAMS = {"stop_loss": 1.5, "vol_max": 2.0}


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


def _rising(x, n):
    """Pine rising(x, n): x above every one of its previous n values."""
    return x > x.shift(1).rolling(n).max()


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    ema = c.ewm(span=20, adjust=False).mean()
    sma, sma_slow = c.rolling(100).mean(), c.rolling(200).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    vol = _rma(tr, 14) / c * 100
    enter = ((vol < p["vol_max"]) & _rising(sma_slow, 10) & _rising(macd, 3) & _rising(ema, 2)
             & _rising(sma, 3) & (ema > sma) & (sma < c)).to_numpy()
    e1, s1 = ema.shift(1), sma.shift(1)
    x_dn = ((e1 < s1) & (e1.shift(1) >= s1.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    sl = p["stop_loss"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    opened, stop = False, 0.0
    for i in range(m):
        if not opened and enter[i]:
            stop = cv[i] * (1 - sl)
            opened = True
        if opened and (cv[i] <= stop or x_dn[i]):
            opened = False
        tgt[i] = 1 if opened else 0
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
