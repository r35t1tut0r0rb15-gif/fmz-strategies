"""SMA 21 / 50 / 200 alignment breakouts, 10-minute bars: a close above all three SMAs with RSI 14 over 50 and the high over the previous 2-bar highest close goes long; the mirror goes short; reversing.
Port of FMZ strategy #439981 "MT Coordination Trading Strategy" (Best Scalping Strategy Period (TMA)).

FMZ source id: 439981

Source
    https://www.fmz.com/strategy/439981 (PineScript v5, FMZ last modified 2024-01-25 15:06:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-240), SMA 21 / 50 / 200; RSI 14; "fractals" length 2; leverage 1, 100 % of the portfolio
    buy = close > sma21 and close > sma50 and close > sma200 and rsi > 50 and high > highest(close, 2)[1];  sell mirror with low < lowest(close, 2)[1];  entry Buy / entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Williams fractals" are the highest / lowest close of 2 bars, as coded. The two setups cannot
      share a bar. strategy.entry reverses: REVERSAL INTENDED. The equity-based quantity is sizing. FREQ
      = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA sides, RSI and close-channel breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the leverage and portfolio share stored.
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

NAME = "fmz_439981_sma_stack_rsi50_close_break"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma200_length": [200, 100],
    "williams_length": [2, 5],
}
DEFAULT_PARAMS = {"sma200_length": 200, "williams_length": 2, "sma21_length": 21, "sma50_length": 50, "rsi_length": 14}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s1, s2, s3 = (c.rolling(int(p[k])).mean() for k in ("sma21_length", "sma50_length", "sma200_length"))
    r = _rsi(c, int(p["rsi_length"]))
    w = int(p["williams_length"])
    fu, fd = c.rolling(w).max().shift(1), c.rolling(w).min().shift(1)
    buy = (c > s1) & (c > s2) & (c > s3) & (r > 50) & (h > fu)
    sell = (c < s1) & (c < s2) & (c < s3) & (r < 50) & (lo < fd)
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
