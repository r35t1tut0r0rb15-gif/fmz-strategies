"""Red "panic" candles breaking a twice-touched resistance in the opening hours, 1-hour bars, long only: in 08:00-12:00 or 15:30-19:00 UTC, a red candle closing over the oldest 20-bar swing high (with at least two swing highs in the window), near the SMA 14, over the EMA 10 and EMA 200, with RSI 7 over 30, ADX 7 over 10 and not two red candles before it, buys from flat. The 2 / 4 ATR bracket is re-sent every bar from the latest close and is not ported (pending), so the first long is held.
Port of FMZ strategy #471686 "Post-Open-Breakout-Trading-Strategy-with-Dynamic-ATR-Based-Position-Management-基于ATR动态管理的开市突破交易策略" (Post-Open Long Strategy with ATR-based Stop Loss and Take Profit).

FMZ source id: 471686

Source
    https://www.fmz.com/strategy/471686 (PineScript v5, FMZ last modified 2024-11-12 14:26:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-186), BB 14 basis (SMA 14), 1 % near-basis band; EMA 10 / 200; RSI 7 > 30; DMI 7 / 7, ADX > 10; resistance = oldest swing high of the last 20 bars, >= 2 swing highs; hours 8-12 and 15:30-19 (exchange time); ATR 14 stop 2 x, target 4 x from the current close
    breakout and near basis in hours and close > ema10 and rsi > 30 and adx > 10 and not (red[1] and red[2]) and close > ema200 and red candle in hours and no open trade -> entry Long
    while open: exit(stop = close - 2 atr, limit = close + 4 atr)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loop over the last 20 bars keeps the last swing high it meets, which is the oldest one in the
      window; with no swing high the previous level is kept (var). The hours are the bar's UTC open
      (the Binance exchange time). The bracket is re-sent on every bar from that bar's close, so its
      levels move after entry: stops() cannot express a level re-set every bar, so it is described here
      and kept pending (as #438034, mark trailing_stop_pending). With no other exit and entries only
      from flat, the port holds the first long to the end of the data until the bracket is ported. Long
      only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, session breakouts of a touched resistance with trend filters; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR bracket inputs stored.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 08:00-12:00 and 15:30-19:00 UTC on the bar open.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471686_session_panic_candle_resistance_breakout_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def simulate(bars_df, **params):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ix = bars_df.index
    hr, mn = ix.hour, ix.minute
    sess = pd.Series(((hr >= 8) & (hr < 12)) | ((hr == 15) & (mn >= 30)) | ((hr >= 16) & (hr < 19)), index=ix)
    sma = c.rolling(14).mean()
    lateral = ((c - sma).abs() < 0.01 * c) & sess
    ema10, ema200 = c.ewm(span=10, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    r = _rsi(c, 7)
    adx = _dmi(bars_df, 7)[2]
    q = ((h.shift(1) > h.shift(2)) & (h.shift(1) > h)).to_numpy()   # swing high at the bar before
    touches = pd.Series(q.astype(float), index=ix).rolling(20, min_periods=1).sum().to_numpy()
    hv = h.to_numpy(dtype=float)
    m = len(hv)
    level = np.full(m, np.nan)
    lv = np.nan
    for t in range(m):
        for j in range(max(t - 19, 1), t + 1):    # the oldest swing high of the last 20 bars
            if q[j]:
                lv = hv[j - 1]
                break
        level[t] = lv
    red = c < o
    breakout = (c > pd.Series(level, index=ix)) & (pd.Series(touches, index=ix) >= 2)
    no_pull = ~(red.shift(1, fill_value=False) & red.shift(2, fill_value=False))
    le = (breakout & lateral & (c > ema10) & (r > 30) & (adx > 10) & no_pull & (c > ema200)
          & red & sess)
    false = pd.Series(False, index=ix)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
