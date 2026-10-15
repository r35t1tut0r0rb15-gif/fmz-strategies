"""Detrended synthetic price (HPotter D_DSP): EMA 14 minus EMA 28 of hl2; above an upper band goes
long, below a lower band goes short (always in the market after the first signal).
Port of FMZ strategy #427280 "Dual Moving Average Trading Strategy Based on Detrended Synthetic Price".

FMZ source id: 427280

Source
    https://www.fmz.com/strategy/427280 (PineScript v2, FMZ last modified 2023-09-19 17:13:28).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 183-202), length 14, SellBand 25, BuyBand -25, reverse off
    dsp = ema(hl2, 14) - ema(hl2, 28)
    pos = dsp > 25 ? 1 : dsp < -25 ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the bands +-25 are price units (instrument-specific). They become
      +- `band_atr` x Wilder ATR(14) of the same bar. On the source's 1-minute BTC bars 25 USD is
      about 1-3 ATR (judgement, stated before any backtest).
    * As written, the band named SellBand buys (above it -> long) and BuyBand sells.
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit bands -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427280_detrended_synthetic_price"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "band_atr": [2.0, 1.0, 4.0],
}
DEFAULT_PARAMS = {"length": 14, "band_atr": 2.0, "atr_length": 14}


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


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
    n = int(p["length"])
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    dsp = (hl2.ewm(span=n, adjust=False).mean() - hl2.ewm(span=2 * n, adjust=False).mean()).to_numpy()
    band = (p["band_atr"] * _atr(bars_df, int(p["atr_length"]))).to_numpy()
    m = len(dsp)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if dsp[i] > band[i]:
            pos = 1
        elif dsp[i] < -band[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
