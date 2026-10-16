"""Rising RSI of a smoothed low outside sideways markets, 2-hour bars: the RSI 14 of EMA 19 of the low above its two
previous values, with %B not sideways and a 2-bar ROC beyond 0.5 %, goes long; otherwise (still moving and not
sideways) goes short.
Port of FMZ strategy #429506 "RSI上升的加密趋势策略RSI-Rising-Crypto-Trending-Strategy" (RSI Rising).

FMZ source id: 429506

Source
    https://www.fmz.com/strategy/429506 (PineScript v4, FMZ last modified 2023-10-17 17:08:31).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 177-227), EMA 19 of low, RSI 14, BB 20 x 1 (%B stdev 21 <= 0.1 = sideways), ROC 2 beyond 0.5 %
    rsiClose = rsi(ema(low, 19), 14); moving = |ema(roc(close, 2), 1)| > 0.5; sideways = 0 < %B < 1 and stdev(%B, 21) <= 0.1
    rising(rsiClose, 2) and not sideways and moving -> entry long; not rising and not sideways and moving -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, 2) = x above each of its two previous values; ema(x, 1) is x itself.
    * strategy.entry reverses: REVERSAL INTENDED. The dates are unused. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI, %B and percentage tests only.
    3 crypto-exchange-only: no ("Crypto" in the name only; exchange pair in the header).
    4 signals only: the strategy() 100 % of equity and commission stored.
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

NAME = "fmz_429506_rsi_rising_not_sideways"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [19, 10],
    "smooth": [14, 7],
}
DEFAULT_PARAMS = {"periods": 19, "smooth": 14, "bb_length": 20, "bb_mult": 1.0, "bbr_len": 21,
                  "bbr_thresh": 0.1, "roc_len": 2, "pcnt": 1.0}


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
    lo, c = bars_df["low"], bars_df["close"]
    n = int(p["bb_length"])
    basis, dev = c.rolling(n).mean(), p["bb_mult"] * c.rolling(n).std(ddof=0)
    bbr = (c - (basis - dev)) / (2 * dev).replace(0.0, np.nan)
    sideways = (bbr > 0) & (bbr < 1) & (bbr.rolling(int(p["bbr_len"])).std(ddof=0) <= p["bbr_thresh"])
    k = int(p["roc_len"])
    roc = 100 * (c - c.shift(k)) / c.shift(k)
    moving = (roc > p["pcnt"] / 2) | (roc < -p["pcnt"] / 2)
    r = _rsi(lo.ewm(span=int(p["periods"]), adjust=False).mean(), int(p["smooth"]))
    rising = r > pd.concat([r.shift(1), r.shift(2)], axis=1).max(axis=1, skipna=False)
    ok = ~sideways & moving
    long_e = (rising & ok).astype(bool)
    short_e = (~rising & ok).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
