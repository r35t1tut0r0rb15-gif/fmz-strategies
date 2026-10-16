"""ATR band reversal, 5-minute bars: the close dropping through the lower band (EMA 26 - 2 ATR) goes
long, the close rising through the upper band (EMA 26 + 1 ATR) goes short.
Port of FMZ strategy #427925 "ATR Trailing Stop Strategy" (ATR Strategy FOREX, Investoz).

FMZ source id: 427925

Source
    https://www.fmz.com/strategy/427925 (PineScript v4, FMZ last modified 2023-09-26 20:23:13).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 152-184), length 26, multipliers 1 / 2
    bull = ema(close, 26) + atr(26); bear = ema(close, 26) - 2 atr(26)
    crossunder(close, bear) -> entry long (close short); crossunder(bull, close) -> entry short (close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * sma(close, 1) is the close. The date window is open (startTimeOk() is true).
    * The closes coincide with the opposite entries: REVERSAL INTENDED. Nothing trails despite the title.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: DG427925 (3 members, best partner #442844, Jaccard 0.899); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427925_atr_band_reversal"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [26, 50],
    "mul": [1.0, 2.0],
    "mullow": [2.0, 1.0],
}
DEFAULT_PARAMS = {"len": 26, "mul": 1.0, "mullow": 2.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len"])
    avg = c.ewm(span=n, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n)
    bull, bear = avg + atr * p["mul"], avg - atr * p["mullow"]
    long_s = ((c < bear) & (c.shift(1) >= bear.shift(1))).to_numpy()
    short_s = ((bull < c) & (bull.shift(1) >= c.shift(1))).to_numpy()
    m = len(long_s)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_s[i]:
            pos = 1
        elif short_s[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
