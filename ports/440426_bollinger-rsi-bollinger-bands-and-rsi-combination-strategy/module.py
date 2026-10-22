"""Bollinger squeeze longs, 1-hour bars, long only: while 2 x ATR(20) is wider than 2 Bollinger deviations, a non-rising ATR with both RSI 10 and RSI 14 rising goes long from flat; a low at or under the
ratcheting low - 2 ATR line, or RSI 14 above 70 with RSI 10 above it, closes.
Port of FMZ strategy #440426 "收缩带Bollinger与RSI组合策略Bollinger-Bands-and-RSI-Combination-Strategy" ([KL] BOLL + RSI Strategy).

FMZ source id: 440426

Source
    https://www.fmz.com/strategy/440426 (PineScript v4, FMZ last modified 2024-01-30 15:15:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-217), BB 20 / 2; ATR 20 x 2; ATR look-back 1; overbought 70 on RSI 14; date window from 2016
    flat: stop = low - 2 atr;  long: stop = max(stop, low - 2 atr);  entry when atr2 <= atr2[1] and rsi10, rsi14 rising and 2 atr > 2 sd and flat (entry price = close, stop = low - 2 atr)
    long: close Long when low <= stop (below or above the entry price) or (rsi14 > 70 and rsi10 > rsi14);  flat and not squeezing: entry price and stop reset to 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line is a close test, not an order: the bar's own low is checked against the line
      just raised by that bar (which only fires when the low reaches the earlier line), and the close
      goes at the next open. The position tests use the held position, so the exit tests start on the
      fill bar. The date window is dropped. Pine's stdev is the population deviation. Long only. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested trailing line.
    2 generic: PASS, ATR / Bollinger squeeze and RSI slopes.
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

NAME = "fmz_440426_boll_squeeze_rsi_slope_atr_line"
FAMILY = "volatility_squeeze"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 14],
    "overbought": [70, 80],
}
DEFAULT_PARAMS = {"length": 20, "overbought": 70, "atr_lookback": 1}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, lo = bars_df["close"], bars_df["low"]
    n = int(p["length"])
    sd2 = 2 * c.rolling(n).std(ddof=0)
    ax = 2 * _atr(bars_df, n)
    avg = ax.rolling(int(p["atr_lookback"])).mean()
    r10, r14 = _rsi(c, 10), _rsi(c, 14)
    squeeze = (ax > sd2).to_numpy()
    entry = ((avg <= avg.shift(1)) & (r10 > r10.shift(1)) & (r14 > r14.shift(1))).to_numpy() & squeeze
    ob = ((r14 > float(p["overbought"])) & (r10 > r14)).to_numpy()
    lv, axv = lo.to_numpy(dtype=float), ax.to_numpy(dtype=float)
    m = len(lv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, sl = False, 0.0
    for i in range(m):
        line = lv[i] - axv[i]
        if not held:
            sl = line
        elif not np.isnan(line):
            sl = line if np.isnan(sl) else max(sl, line)
        nxt = held
        if entry[i] and not held and i + 1 < m:
            le[i], nxt = True, True
            sl = line
        if held and (lv[i] <= sl or ob[i]):
            lx[i], nxt = True, False
        if not held and not squeeze[i]:
            sl = 0.0
        held = nxt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
