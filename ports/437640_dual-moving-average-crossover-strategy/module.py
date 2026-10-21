"""SMA 50 / 100 crossings with a 4-ATR stop, 1-minute bars: the fast SMA crossing over the slow one goes long with a stop 4 ATR 14 under the signal close, crossing under goes short with the mirror stop; reversing.
Port of FMZ strategy #437640 "Dual Moving Average Crossover Strategy" (SMA and ATR Strategy).

FMZ source id: 437640

Source
    https://www.fmz.com/strategy/437640 (PineScript v5, FMZ last modified 2024-01-04 15:03:14).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-166), SMA 50 / 100, ATR 14 x 4
    longCondition = crossover(sma 50, sma 100) -> entry Buy, exit(stop = close - 4 atr);  shortCondition = crossunder -> entry Sell, exit(stop = close + 4 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is set once at the signal bar: sl_stop = 4 x ATR(14) / close of the signal bar, shifted one
      bar inside stops() and re-based on the fill. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437640_sma_cross_atr_stop"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [50, 20],
    "atr_mult": [4.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 100, "atr_len": 14, "atr_mult": 4.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
