"""Connors RSI 2 pullback, 1-hour bars, long only: RSI 2 under 10 with the close above its SMA 200 and the SMA 4 of RSI
under 30 goes long; a close above the SMA 5 closes the long.
Port of FMZ strategy #430374 "Oscillation Breakthrough Strategy" (RSI Strategy).

FMZ source id: 430374

Source
    https://www.fmz.com/strategy/430374 (PineScript v3, FMZ last modified 2023-10-27 16:32:19).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 177-248), RSI 2, SMA 5 / 200, RSI average 4 under 30 (filter on), stop off
    rsi(close, 2) < 10 and close > sma(close, 200) and sma(rsi, 4) < 30 -> entry long
    close > sma(close, 5) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: the RSI-average filter on, the 10 % stop off (option, not ported).
    * close_all acts on the position held at the start of the bar: a bar that both signals and
      closes ends flat when already long, long when flat.
    * Long only; Opposite entries cannot occur. testPeriod() is always true. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430374_connors_rsi2_pullback_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_level": [10, 5],
    "long_ma": [200, 100],
}
DEFAULT_PARAMS = {"rsi_len": 2, "rsi_level": 10, "short_ma": 5, "long_ma": 200, "mrsi_len": 4, "mrsi_level": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


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
    r = _rsi(c, int(p["rsi_len"]))
    mrsi = r.rolling(int(p["mrsi_len"])).mean()
    entry = ((r < p["rsi_level"]) & (c > c.rolling(int(p["long_ma"])).mean()) & (mrsi < p["mrsi_level"])).to_numpy()
    ex = (c > c.rolling(int(p["short_ma"])).mean()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if entry[i]:
            pos = 1
        if ex[i] and start == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
