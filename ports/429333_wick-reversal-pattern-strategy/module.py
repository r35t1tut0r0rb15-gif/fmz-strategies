"""Long-wick reversal candles, 3-minute bars: a large candle (range >= 1.1 x its 50-bar RMA) with a lower wick
3.25x the body and the close in the top 35 % goes long; the mirror (upper wick) goes short.
Port of FMZ strategy #429333 "Wick Reversal Pattern Strategy" (Wick Reversal Signal).

FMZ source id: 429333

Source
    https://www.fmz.com/strategy/429333 (PineScript v4, FMZ last modified 2023-10-16 08:58:12).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 132-152), wick multiplier 3.25, body percentage 0.35, bars back 50, body multiplier 1.1
    long: green with open - low >= 3.25 body, red with close - low >= 3.25 body, or a doji (|close - open| < 0.01, close != high)
          with range >= 3.25 (high - close); each with high - close <= 0.35 range and range >= 1.1 rma(range, 50) -> entry long
    short: the mirror on the upper wick -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the doji test |close - open| < 0.01 (price units) becomes |close - open| <
      doji_atr x Wilder ATR(14); 0.01 USD on 3-minute BTC is about 0.0005 ATR (judgement before any
      backtest).
    * strategy.entry reverses: REVERSAL INTENDED. If both fire on one bar the long (first order) is kept.
      FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit doji threshold -> an ATR multiple.
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

NAME = "fmz_429333_wick_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wick_mult": [3.25, 2.5],
    "body_mult": [1.1, 1.5],
}
DEFAULT_PARAMS = {"wick_mult": 3.25, "body_pct": 0.35, "bars_back": 50, "body_mult": 1.1, "doji_atr": 0.0005,
                  "atr_length": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    w, bp = p["wick_mult"], p["body_pct"]
    rng = h - lo
    big = rng >= _rma(rng, int(p["bars_back"])) * p["body_mult"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    doji = (c - o).abs() < p["doji_atr"] * _rma(tr, int(p["atr_length"]))
    top = (h - c) <= rng * bp
    bot = (c - lo) <= rng * bp
    long_s = (((c > o) & ((o - lo) >= (c - o) * w)) | ((c < o) & ((c - lo) >= (o - c) * w))
              | (doji & (c != h) & (rng >= (h - c) * w))) & top & big
    short_s = (((c < o) & ((h - o) >= (o - c) * w)) | ((c > o) & ((h - c) >= (c - o) * w))
               | (doji & (c != lo) & (rng >= (c - lo) * w))) & bot & big
    long_e = long_s.astype(bool)
    short_e = (short_s & ~long_s).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
