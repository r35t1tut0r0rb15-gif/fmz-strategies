"""Capitulation-bar dip buys, 15-minute bars, long only: a large red candle stretched more than twice its usual distance from the SMA 10, making a lower body low with the 2-bar RSI under 10, goes long;
a green candle with an ordinary body and the high above the SMA 5 closes.
Port of FMZ strategy #441185 "Quantitative Trading Strategy for Bottom Reversal" (MarketBottom).

FMZ source id: 441185

Source
    https://www.fmz.com/strategy/441185 (PineScript v3, FMZ last modified 2024-02-06 15:16:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-164), fast RSI 2 (Pine formula); body filter SMA 10 x 1.5; distance SMA 100 x 2; exit SMA 5
    up = close < open and |close - sma10| > 2 sma(|close - sma10|, 100) and min(open, close) < its value 1 bar back and fastrsi < 10 and body > 1.5 sma(body, 10) -> entry Long
    exit = high > sma(close, 5) and close > open and body > sma(body, 10) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry needs a red candle and the exit a green one, so they never meet on one bar. Long only. No
      sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, body, distance and fast RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441185_capitulation_bar_fast_rsi_dip_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_level": [10, 20],
    "dist_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"rsi_level": 10, "dist_mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, c = bars_df["open"], bars_df["high"], bars_df["close"]
    fr = _rsi(c, 2)
    body = (c - o).abs()
    ab = body.rolling(10).mean()
    dist = (c - c.rolling(10).mean()).abs()
    mn = pd.concat([o, c], axis=1).min(axis=1)
    up = (c < o) & (dist > dist.rolling(100).mean() * float(p["dist_mult"])) & (mn < mn.shift(1)) \
        & (fr < float(p["rsi_level"])) & (body > ab * 1.5)
    ex = (h > c.rolling(5).mean()) & (c > o) & (body > ab)
    false = pd.Series(False, index=c.index)
    return up, ex, false, false.copy()


def portfolio_kwargs(**params):
    return {}
