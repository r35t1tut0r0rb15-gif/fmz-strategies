"""SMA trend swing (Zer3192): a smoothed close (SMA 20 of (close + SMA 5)) / 2 drives a swing
machine that flips down when it falls 5 % below its running high and up when it rises 5 % above its
running low; up-flips go long, down-flips go short (always in).
Port of FMZ strategy #366389 "SMA Trend".

Source
    https://www.fmz.com/strategy/366389 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-05 06:51:08). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 36-154), SMA length 20, factor 0.05
    c5 = sma(sma(close, 1) + sma(close, 5), 20) / 2
    x = c5 - log(10), n = c5 + log(10) -> swing machine (hb / lb / trend)
    buy = first trend up-flip after a down-flip -> entry long; sell mirrors -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the +- log(10) = 2.303 offset is in price units. It becomes +- off_atr x
      ATR(14) (0 drops it; on BTC 2.3 is about 0 ATR).
    * buy / sell (crossover of the last flip times) equal the trend flips, since flips alternate.
    * The swing machine follows Pine's nz() semantics.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header (spot pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366389_sma_swing_trend"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "len_c": [10, 20, 40],
    "factor": [0.02, 0.05],
    "off_atr": [0.0, 0.25],
}
DEFAULT_PARAMS = {"len_c": 20, "factor": 0.05, "off_atr": 0.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _hb_lb_trend(n, x, factor):
    """Zer3192's swing machine (Pine nz() semantics): hb ratchets up with x while trend > 0 and
    flips to -1 when n falls `factor` below hb[1]; lb ratchets down with n while trend < 0 and
    flips to 1 when x rises `factor` above lb[1]. Returns (trend, v = hb if 1, lb if -1)."""
    n, x = np.asarray(n, dtype=float), np.asarray(x, dtype=float)
    m = len(n)
    hb, lb = np.full(m, np.nan), np.full(m, np.nan)
    tr = np.zeros(m)
    nz = lambda a: 0.0 if np.isnan(a) else a
    for i in range(m):
        hb1 = hb[i - 1] if i else np.nan
        lb1 = lb[i - 1] if i else np.nan
        h_, l_, t = nz(hb1), nz(lb1), (tr[i - 1] if i else 0.0)
        if i == 0:
            l_, h_ = n[i], x[i]
        elif i == 1:
            if x[i] >= hb1:
                h_, t = x[i], 1.0
            else:
                l_, t = n[i], -1.0
        elif tr[i - 1] > 0:
            if x[i] >= hb1:
                h_ = x[i]
            elif n[i] < hb1 - hb1 * factor:
                l_, t = n[i], -1.0
        else:
            if n[i] <= lb1:
                l_ = n[i]
            elif x[i] > lb1 + lb1 * factor:
                h_, t = x[i], 1.0
        hb[i], lb[i], tr[i] = h_, l_, t
    v = np.where(tr == 1, hb, np.where(tr == -1, lb, np.nan))
    return tr, v


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    c5 = (c + c.rolling(5).mean()).rolling(int(p["len_c"])).mean() / 2
    off = p["off_atr"] * _atr_pine(bars_df, ATR_LEN)
    tr, _ = _hb_lb_trend((c5 + off).to_numpy(), (c5 - off).to_numpy(), p["factor"])
    prev = np.concatenate([[np.nan], tr[:-1]])
    return _always_in((tr == 1) & (prev == -1), (tr == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
