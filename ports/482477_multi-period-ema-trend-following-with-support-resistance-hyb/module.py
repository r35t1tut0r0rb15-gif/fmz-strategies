"""Closes beyond the prior 9-bar extreme, or beyond the EMA 20 in a trending EMA 20 / 50 state (more than 1 ATR
apart), keep the strategy long or short, with a 10 ATR stop from the latest close, hourly bars.
Port of FMZ strategy #482477 "多周期均线趋势跟踪与支阻系统结合的混合交易策略-Multi-Period-EMA-Trend-Following-with-Support-Resistance-Hybrid-Trading-System" (Multi-Strategy Trader v1).

FMZ source id: 482477

Source
    https://www.fmz.com/strategy/482477 (PineScript v6, FMZ last modified 2025-02-18 15:52:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 124-155), look-back 9, ATR 14 x 10, EMA 20 / 50
    long = close > highest(high, 9)[1] or (|ema20 - ema50| > ATR and ema20 > ema50 and close > ema20)
    short = close < lowest(low, 9)[1] or (|ema20 - ema50| > ATR and ema20 < ema50 and close < ema20)
    long and position <= 0 -> entry long; short and position >= 0 -> entry short
    every bar while held: exit(stop = close -/+ 10 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-issued every bar from the current close and ATR (a moving level): fixed at the entry as
      10 ATR / close of the signal bar, shifted one bar inside stops() and re-based on the fill; mark
      trailing_stop_pending.
    * Both entry tests read the position at the bar's start: on a bar with both signals the short (written later)
      wins when flat or long, the long when short. simulate() mirrors the house stop from the fill (as #430254) so
      this choice sees the position the engine holds.
    * The script's credit line (a name, phone number and web address) is not reproduced in the module NAME.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, rolling extremes, EMAs and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the stop via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482477_breakout_or_ema_trend_state_wide_atr_stop"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [9, 20],
    "stop_mult": [10.0, 5.0],
}
DEFAULT_PARAMS = {"lookback": 9, "atr_len": 14, "stop_mult": 10.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _fracs(bars_df, p):
    return (p["stop_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy()


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    hs, ls, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, int(p["atr_len"]))
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    trending = (e20 - e50).abs() > atr
    n = int(p["lookback"])
    long_c = ((c > hs.rolling(n).max().shift(1)) | (trending & (e20 > e50) & (c > e20))).to_numpy()
    short_c = ((c < ls.rolling(n).min().shift(1)) | (trending & (e20 < e50) & (c < e20))).to_numpy()
    sl = _fracs(bars_df, p)
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house stop from the fill price
            e = o[entry_i]
            if (pos == 1 and lo[i] <= e * (1 - s_)) or (pos == -1 and h[i] >= e * (1 + s_)):
                pos = 0
        if i + 1 >= m or np.isnan(sl[i]):
            continue
        go_l, go_s = long_c[i] and pos <= 0, short_c[i] and pos >= 0
        if go_l and go_s:                                   # the later call decides the final side
            side = 1 if pos == -1 else -1
        elif go_l:
            side = 1
        elif go_s:
            side = -1
        else:
            continue
        if side != pos:
            (le if side == 1 else se)[i] = True
            pos, entry_i, s_ = side, i + 1, sl[i]
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": pd.Series(_fracs(bars_df, p), index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
