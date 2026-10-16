"""AK RSI 2, as written: above SMA 200 with the close under SMA 5 and RSI(2) under 5 goes long; below
SMA 200 with the close over SMA 5 and RSI(2) over 90 goes short. Both close_all lines act on any open
position (close above SMA 5, or below it), so a position is closed on the bar after its fill unless
the close sits exactly on SMA 5.
Port of FMZ strategy #427458 "AK Dual RSI Breakout Strategy".

FMZ source id: 427458

Source
    https://www.fmz.com/strategy/427458 (PineScript v2, FMZ last modified 2023-09-21 11:51:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 149-167), RSI 2, SMA 5 / 200, levels 5 / 90
    close > sma200 and close < sma5 and rsi2 < 5 -> entry long; close_all(when close > sma5)
    close < sma200 and close > sma5 and rsi2 > 90 -> entry short; close_all(when close < sma5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported AS WRITTEN: close_all is not tied to a side, so either test closes whatever is open
      (Connors' RSI-2 evidently meant "close the long above SMA 5, the short below it"; that version
      is a decision owed). A close only acts on a position open when the bar's orders are placed.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427458_ak_rsi2_as_written"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_level": [5, 10],
    "short_level": [90, 95],
    "ma_long": [200, 100],
}
DEFAULT_PARAMS = {"rsi_length": 2, "ma_short": 5, "ma_long": 200, "long_level": 5, "short_level": 90}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    m5 = c.rolling(int(p["ma_short"])).mean().to_numpy()
    m200 = c.rolling(int(p["ma_long"])).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    long_c = (cv > m200) & (cv < m5) & (r < p["long_level"])
    short_c = (cv < m200) & (cv > m5) & (r > p["short_level"])
    close_any = (cv > m5) | (cv < m5)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        held = pos
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif held != 0 and close_any[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
