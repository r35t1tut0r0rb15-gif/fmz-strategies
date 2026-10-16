"""Supertrend turn with RSI and ADX filters, 2-hour bars, long only: the supertrend (ATR 19 x 3) turning up with RSI 21
under 75, RSI 3 over 65, RSI 28 over 49 and ADX 7 over 21 goes long; the supertrend turning down or RSI 10 under 42
closes it.
Port of FMZ strategy #430585 "Tesla Supertrend Strategy" (TSLA 1.8k Strategy).

FMZ source id: 430585

Source
    https://www.fmz.com/strategy/430585 (PineScript v5, FMZ last modified 2023-10-30 15:46:31).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-218), supertrend 19 / 3, ADX 7 / 7, RSI 21 / 3 / 28 / 10
    change(direction) < 0 and rsi21 < 75 and rsi3 > 65 and rsi28 > 49 and adx > 21 -> entry long
    change(direction) > 0 or rsi10 < 42 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction falls from 1 to -1 when the trend turns up. ADX as the source's
      dirmov (Wilder averages; fixnan over a zero true range).
    * The close is written after the entry: a bar that both qualifies and closes ends flat when
      already long, long when flat.
    * Long only; Opposite entries cannot occur. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands, RSI and ADX levels.
    3 crypto-exchange-only: no ("Tesla" in the title only; exchange pair in the header).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430585 (4 members, best partner #436541, Jaccard 0.836); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430585_supertrend_rsi_adx_long"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [19, 10],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 19, "factor": 3.0, "adx_len": 7, "di_len": 7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    return x.ewm(alpha=1 / n, adjust=False).mean()


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return _rma(tr, n)


def _supertrend_dir(bars, factor, atr_period):
    """direction of ta.supertrend(factor, atrPeriod) as in Pine v5 (negative = up-trend)."""
    atr = _atr(bars, atr_period).to_numpy()
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hl2 = (h + lo) / 2
    m = len(c)
    dirn = np.full(m, np.nan)
    lower_prev = upper_prev = 0.0
    st_prev = np.nan
    for i in range(m):
        lower, upper = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        if i > 0:
            if not (lower > lower_prev or c[i - 1] < lower_prev):
                lower = lower_prev
            if not (upper < upper_prev or c[i - 1] > upper_prev):
                upper = upper_prev
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_prev == upper_prev:
            d = -1 if c[i] > upper else 1
        else:
            d = 1 if c[i] < lower else -1
        st_prev = lower if d == -1 else upper
        dirn[i] = d
        lower_prev = 0.0 if np.isnan(lower) else lower
        upper_prev = 0.0 if np.isnan(upper) else upper
    return pd.Series(dirn, index=bars.index)


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _adx(h, lo, c, di_len, adx_len):
    up, down = h.diff(), -lo.diff()
    plus_dm = (((up > down) & (up > 0)).astype(float) * up).where(up.notna())
    minus_dm = (((down > up) & (down > 0)).astype(float) * down).where(down.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, di_len).replace(0.0, np.nan)
    plus = _fixnan(100 * _rma(plus_dm, di_len) / atr)
    minus = _fixnan(100 * _rma(minus_dm, di_len) / atr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


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
    d = _supertrend_dir(bars_df, float(p["factor"]), int(p["atr_period"]))
    dch = d.diff()
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    entry = ((dch < 0) & (_rsi(c, 21) < 75) & (_rsi(c, 3) > 65) & (_rsi(c, 28) > 49) & (adx > 21)).to_numpy()
    ex = ((dch > 0) | (_rsi(c, 10) < 42)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if entry[i]:
            pos = 1
        if ex[i] and start == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
