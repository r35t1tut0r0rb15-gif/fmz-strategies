"""Noro's Anti RSI, 15-minute bars: from flat, a red bar just after RSI 14 leaves overbought (> 75) goes
long and a green bar just after it leaves oversold (< 25) goes short (counter-signals); a long closes on
a green bar with a real body, a short on a red one.
Port of FMZ strategy #428051 "RSI Signal Tracking Reversal Trading Strategy" (Noro's Anti RSI v1.0).

FMZ source id: 428051

Source
    https://www.fmz.com/strategy/428051 (PineScript v2, FMZ last modified 2023-09-28 10:54:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 194-265), RSI 14 (Wilder), limit 25
    up1 = red bar and flat and overbought[1] and not overbought -> entry long
    dn1 = green bar and flat and oversold[1] and not oversold -> entry short
    up2 / dn2 add to an open position (pyramiding 0: ignored)
    exit = (long and green bar or short and red bar) and body > sma(body, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries need a flat position. Opposite entries cannot occur (the close_all before an entry
      only applies to a short, which up1 / up2 never meet).
    * Martingale (off), capital % and the long / short switches are sizing; the date window is dropped.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and body ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot, martingale and capital inputs stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428051_noro_anti_rsi"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [14, 7],
    "rsi_limit": [25, 15],
}
DEFAULT_PARAMS = {"rsi_period": 14, "rsi_limit": 25, "body_len": 10}


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
    o, c = bars_df["open"], bars_df["close"]
    d = c.diff()
    n = int(p["rsi_period"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    lim = p["rsi_limit"]
    ob, os_ = (rsi > 100 - lim).to_numpy(), (rsi < lim).to_numpy()
    body = (c - o).abs()
    big = (body > body.rolling(int(p["body_len"])).mean() / 2).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        start = pos
        if start == 0:
            if red[i] and ob[i - 1] and not ob[i]:
                pos = 1
            elif green[i] and os_[i - 1] and not os_[i]:
                pos = -1
        elif start == 1 and green[i] and big[i]:
            pos = 0
        elif start == -1 and red[i] and big[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
