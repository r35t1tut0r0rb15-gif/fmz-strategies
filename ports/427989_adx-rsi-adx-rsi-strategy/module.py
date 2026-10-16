"""ADX + RSI, reversed (the source default), 15-minute bars: with ADX(14) under 30 (no trend), an RSI(7)
above 80 goes LONG and an RSI(7) below 30 goes SHORT (the "Reverse Trades" switch is on by default).
Port of FMZ strategy #427989 "ADX RSI Strategy" (ADX + RSI Strat).

FMZ source id: 427989

Source
    https://www.fmz.com/strategy/427989 (PineScript v4, FMZ last modified 2023-09-27 16:27:39).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 191-253), RSI 7 (30 / 80), ADX 14 / 14, level 30, reverse on
    BUY = adx < 30 and rsi < 30; SELL = adx < 30 and rsi > 80
    entry long when (reverse ? SELL : BUY); entry short when (not reverse ? SELL : BUY)
    swing stop / target exits only when "Use Swing Lo/Hi" is on (default off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The defaults are kept: reverse on (fixed, not searched), swing exits off, direction all.
      (The swing levels, when on, would come from the fill bar: not ported.)
    * ADX as written: dirmov with rma(tr) and fixnan; adx = 100 rma(|+DI - -DI| / sum).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (the off swing exits aside).
    2 generic: PASS, oscillator levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the swing exit inputs stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427989_adx_rsi_reversed"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_level": [30, 20],
    "ob": [80, 70],
    "os": [30, 20],
}
DEFAULT_PARAMS = {"rsi_len": 7, "os": 30, "ob": 80, "adx_len": 14, "di_len": 14, "adx_level": 30}


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


def _fixnan(x):
    """Pine fixnan: an na value takes the last non-na value of the same series (past only)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


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
    d = c.diff()
    k = int(p["rsi_len"])
    ru, rd = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + ru / rd)).where(ru != 0, 0.0).where(rd != 0, 100.0).where(ru.notna() & rd.notna())
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    n = int(p["di_len"])
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    calm = adx < p["adx_level"]
    buy = (calm & (rsi < p["os"])).to_numpy()
    sell = (calm & (rsi > p["ob"])).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if sell[i]:            # reverse on: SELL opens the long
            pos = 1
        elif buy[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
