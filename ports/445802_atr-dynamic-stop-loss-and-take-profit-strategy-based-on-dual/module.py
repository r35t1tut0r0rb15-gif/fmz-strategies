"""UT Bot crossings of two ATR trailing lines (1 x ATR 10, 2 x ATR 20), 1-hour bars: the close crossing over either line goes long, crossing under either goes short; the short's take-profit sits on the
wrong side of the market, so each short closes at the next open after its fill; reversing.
Port of FMZ strategy #445802 "基于ATR双重跟踪止损的动态止盈止损策略Dynamic-Stop-Loss-and-Take-Profit-Strategy-Based-on-Dual-ATR-Trailing-Stop" (UT Bot Strategy (two ATR trailing lines)).

FMZ source id: 445802

Source
    https://www.fmz.com/strategy/445802 (PineScript v4, FMZ last modified 2024-03-22 13:52:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-233), key 1 / ATR 10 and key 2 / ATR 20; Heikin Ashi off; take profit close + 65 bodies for both sides; dates 2019-2100 (always true); EMAs plot only
    ts = UT Bot trailing line (nz seeds);  buy_k = close > ts_k and crossover(close, ts_k);  sell_k = close < ts_k and crossover(ts_k, close)
    exit(long, limit = close + 65 |open - close|);  exit(short, limit = close + 65 |open - close|)  (re-sent every bar);  buy1 or buy2 -> entry long;  sell1 or sell2 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing lines follow the script's nz() seeds. ema(src, 1) is the close. The take-profit is
      re-sent every bar at the bar's close plus 65 bodies for BOTH ids: for a long it is a target that
      moves every bar, not expressible (mark trailing_stop_pending); for a short it is a buy limit above
      the price, on the wrong side of the market, so the short closes at the first open after its fill
      bar (the port closes it on that bar's signal, as #439872). When both sides fire, the later short
      wins (as #437773). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long target re-sent (mark); the short's wrong-side target read as a close.
    2 generic: PASS, UT Bot trailing-line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_445802_ut_bot_two_lines_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key1": [1.0, 2.0],
    "key2": [2.0, 3.0],
}
DEFAULT_PARAMS = {"key1": 1.0, "atr1": 10, "key2": 2.0, "atr2": 20}


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


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _ut_line(sv, nloss):
    """xATRTrailingStop as written (nz seeds: the previous value counts as 0 when na)."""
    m = len(sv)
    ts = np.full(m, np.nan)
    for i in range(m):
        prev = ts[i - 1] if i > 0 and not np.isnan(ts[i - 1]) else 0.0
        s1 = sv[i - 1] if i > 0 else np.nan
        if sv[i] > prev and s1 > prev:
            ts[i] = _nmax(prev, sv[i] - nloss[i])
        elif sv[i] < prev and s1 < prev:
            ts[i] = _nmin(prev, sv[i] + nloss[i])
        else:
            ts[i] = sv[i] - nloss[i] if sv[i] > prev else sv[i] + nloss[i]
    return ts


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    sv = c.to_numpy(dtype=float)
    s1 = np.concatenate(([np.nan], sv[:-1]))
    buy = np.zeros(len(sv), dtype=bool)
    sell = np.zeros(len(sv), dtype=bool)
    for key, n in (("key1", "atr1"), ("key2", "atr2")):
        ts = _ut_line(sv, (float(p[key]) * _rma(tr, int(p[n]))).to_numpy())
        t1 = np.concatenate(([np.nan], ts[:-1]))
        with np.errstate(invalid="ignore"):
            buy |= (sv > ts) & (s1 <= t1)
            sell |= (sv < ts) & (t1 <= s1)
    m = len(sv)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sfill = 0, -1
    for i in range(m):
        new = pos
        if buy[i] and pos != 1:
            le[i], new = True, 1
        if sell[i] and pos != -1:
            se[i], le[i], new = True, False, -1     # the later short wins a tie
        if pos == -1 and new == -1 and i >= sfill:
            sx[i], new = True, 0                    # wrong-side buy limit: out at the next open
        if se[i]:
            sfill = i + 1
        pos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
