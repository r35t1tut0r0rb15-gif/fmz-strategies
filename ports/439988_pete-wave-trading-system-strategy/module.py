"""SMA 9 / 22 crossings with momentum and breakout filters, 1-hour bars: an SMA 9 cross over the SMA 22 on a bar that closed up by a minimum step and above the previous 9-bar high goes long; the mirror goes
short; each trade has a 1.5 % stop; reversing; the price-unit filters are read as fractions.
Port of FMZ strategy #439988 "Pete Wave Trading System Strategy" (9:22 5 MIN 15 MIN BANKNIFTY).

FMZ source id: 439988

Source
    https://www.fmz.com/strategy/439988 (PineScript v5, FMZ last modified 2024-01-25 15:36:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-227), SMA 9 / 22; ATR 14 filter 0.5; stop 1.5 %; pullback 0.5; minimum body 0.5; breakout confirmation on
    long = crossover(sma9, sma22) and atr > 0.5 and (pullback or not crossover(close, sma9)) and change(close) >= 0.5 and close > highest(high, 9)[1] -> entry Long, close Short;  short mirror
    exit(stop = avg x (1 - 1.5 %)) / (1 + 1.5 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the ATR filter (0.5), the pullback step (0.5) and the minimum move (0.5) are in price
      units; each becomes a fraction of the close, 0.5 / 42000 (the BTC reading). A pullback needs the
      close to fall while the minimum-move test needs it to rise, so the pullback branch can never
      pass and the cross over the fast SMA must be absent, as written. The stop is a fixed 1.5 % of the
      average (fill) price (sl_stop 0.015). The close of the other side follows a reversing entry and
      changes nothing. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill.
    2 generic: ADAPT, price-unit filters -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent and point inputs stored.
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

NAME = "fmz_439988_pete_wave_sma9_22_breakout_stop"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trailing_stop": [1.5, 3.0],
    "step_frac": [1.19e-05, 0.001],
}
DEFAULT_PARAMS = {"trailing_stop": 1.5, "step_frac": 1.19e-05, "fast": 9, "slow": 22, "atr_len": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n1 = int(p["fast"])
    f, s = c.rolling(n1).mean(), c.rolling(int(p["slow"])).mean()
    k = float(p["step_frac"])
    big = _atr(bars_df, p["atr_len"]) / c > k
    ch = c.diff() / c
    xo_fs = (f > s) & (f.shift(1) <= s.shift(1))
    xu_fs = (f < s) & (f.shift(1) >= s.shift(1))
    xo_cf = (c > f) & (c.shift(1) <= f.shift(1))
    xu_cf = (c < f) & (c.shift(1) >= f.shift(1))
    pb_l = xo_cf & (ch <= -k)
    pb_s = xu_cf & (ch >= k)
    le = xo_fs & big & (pb_l | ~xo_cf) & (ch > 0) & (ch >= k) & (c > h.rolling(n1).max().shift(1))
    se = xu_fs & big & (pb_s | ~xu_cf) & (ch < 0) & (ch <= -k) & (c < lo.rolling(n1).min().shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["trailing_stop"]) / 100}


def portfolio_kwargs(**params):
    return {}
