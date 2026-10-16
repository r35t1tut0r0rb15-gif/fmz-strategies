"""Two MACD histograms and an RSI of the open, 15-minute bars: both histograms above zero with RSI(open)
under 70 goes long, both below zero with RSI(open) over 20 goes short.
Port of FMZ strategy #428693 "多MACD与RSI策略Multiple-MACD-and-RSI-Strategy" (MACDbl RSI).

FMZ source id: 428693

Source
    https://www.fmz.com/strategy/428693 (PineScript v2, FMZ last modified 2023-10-08 14:03:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 138-164), MACD 10/22/9 on close, 21/45/20 on open, RSI 14 of open, 20 / 70
    delta = (ema(close,10) - ema(close,22)) - sma(that, 9); delta2 the same on open with 21 / 45 / 20
    delta > 0 and delta2 > 0 and rsi(open,14) < 70 -> entry long
    delta < 0 and delta2 < 0 and rsi(open,14) > 20 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar's own open is known at its close: reading it is fine. The "signal" line is an SMA (as
      written, not an EMA).
    * `year > 2015` is the author's backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED. A same-direction entry while in a position is
      ignored (pyramiding 0).
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator thresholds and sign tests only.
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

NAME = "fmz_428693_two_macd_rsi_open"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "overbought": [70, 80],
    "oversold": [20, 30],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 22, "signal": 9, "fast2": 21, "slow2": 45, "signal2": 20,
                  "rsi_length": 14, "overbought": 70, "oversold": 20}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, o = bars_df["close"], bars_df["open"]
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    m1 = e(c, p["fast"]) - e(c, p["slow"])
    d1 = m1 - m1.rolling(int(p["signal"])).mean()
    m2 = e(o, p["fast2"]) - e(o, p["slow2"])
    d2 = m2 - m2.rolling(int(p["signal2"])).mean()
    r = _rsi(o, int(p["rsi_length"]))
    long_e = ((d1 > 0) & (d2 > 0) & (r < p["overbought"])).astype(bool)
    short_e = ((d1 < 0) & (d2 < 0) & (r > p["oversold"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
