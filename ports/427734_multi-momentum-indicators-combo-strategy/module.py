"""The Chande momentum 9 crossing zero while five RSI-derived oscillators agree (RMI 30 / 25, a triple-Hull RSI 14, a VWMA-then-double-EMA RSI 14, a triple-EMA RSI 14 and RMI x Hull RSI, all against zero), hourly bars: crossing up with all below zero goes long, crossing down with all above zero goes short; reversing.
Port of FMZ strategy #427734 "Multi Momentum Indicators Combo Strategy" (RMI + Triple HMRSI + Double EVWRSI + TERSI Strategy).

FMZ source id: 427734

Source
    https://www.fmz.com/strategy/427734 (PineScript v4, FMZ last modified 2023-09-24 13:24:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 206-324), CMO 9; RMI 30 / 25; RSI 14 with HMA 7 x 3, VWMA 7 + EMA 7 x 2, EMA 7 x 3; every level 0
    longcondition2 = rmirsi < 0 and rmi3 < 0 and tersi < 0 and devwrsi < 0 and thrsi1 < 0 and crossover(chandeMO, 0) -> entry Buy
    shortcondition2 = all > 0 and crossunder(chandeMO, 0) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every buy / sell line input is 0, as the defaults set. rmirsi = thrsi x rmi3 / 25 has the sign of
      rmi3 (thrsi is an RSI, positive), as written. The Hull averages are Pine's ta.hma (n / 2 as an
      integer, floor(sqrt(n))). The backtest window inputs are not used (testPeriod() is true).
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Chande momentum zero crossings confirmed by RSI-family oscillators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwma(rsi, 7) of the DEVWRSI line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427734_chande_zero_cross_rmi_hull_vwma_ema_rsi_agreement_reversal"
FAMILY = "oscillator_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cmo_length": [9, 14],
    "rmi_length": [30, 20],
}
DEFAULT_PARAMS = {"cmo_length": 9, "rmi_length": 30, "rmi_mom": 25, "len_rsi": 14, "len_ma": 7}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    mom = c.diff()
    n = int(p["cmo_length"])
    sm1, sm2 = mom.clip(lower=0).rolling(n).sum(), (-mom).clip(lower=0).rolling(n).sum()
    cmo = 100 * (sm1 - sm2) / (sm1 + sm2)
    ch = c - c.shift(int(p["rmi_mom"]))
    nr = int(p["rmi_length"])
    up3, dn3 = _rma(ch.clip(lower=0), nr), _rma((-ch).clip(lower=0), nr)
    rmi3 = (100 - 100 / (1 + up3 / dn3)).where(up3 != 0, 0.0).where(dn3 != 0, 100.0).where(up3.notna() & dn3.notna()) - 50
    r = _rsi(c, int(p["len_rsi"]))
    k = int(p["len_ma"])
    thrsi = _hma(_hma(_hma(r, k), k), k)
    thrsi1 = (thrsi - 50) * 10
    vw = (r * v).rolling(k).sum() / v.rolling(k).sum()
    devwrsi = (vw.ewm(span=k, adjust=False).mean().ewm(span=k, adjust=False).mean() - 50) * 5
    tersi = (r.ewm(span=k, adjust=False).mean().ewm(span=k, adjust=False).mean().ewm(span=k, adjust=False).mean() - 50) * 10
    rmirsi = thrsi * rmi3 / 25
    xu = (cmo > 0) & (cmo.shift(1) <= 0)
    xd = (cmo < 0) & (cmo.shift(1) >= 0)
    le = (rmirsi < 0) & (rmi3 < 0) & (tersi < 0) & (devwrsi < 0) & (thrsi1 < 0) & xu
    se = (rmirsi > 0) & (rmi3 > 0) & (tersi > 0) & (devwrsi > 0) & (thrsi1 > 0) & xd
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
