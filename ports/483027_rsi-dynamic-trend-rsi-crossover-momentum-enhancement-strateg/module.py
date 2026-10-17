"""A simplified "supertrend" (SMA 10 -+ 3 ATR 10, chosen by the close against the previous line) with RSI 14 off its
extremes, always in the market, 1-hour bars: a close above the line with RSI above 30 goes long; a close at or below it
with RSI below 70 goes short.
Port of FMZ strategy #483027 "动态趋势RSI交叉动量增强策略-Dynamic-Trend-RSI-Crossover-Momentum-Enhancement-Strategy" (Supertrend + RSI Strategy).

FMZ source id: 483027

Source
    https://www.fmz.com/strategy/483027 (PineScript v5, FMZ last modified 2025-02-21 10:00:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-136), ATR 10, factor 3, RSI 14 (70 / 30)
    upper / lower = sma(close, 10) +- 3 ATR(10); line = close > nz(line[1], close) ? lower : upper
    long = close > line and rsi > 30; short = close <= line and rsi < 70

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is the source's own recursion (not ta.supertrend), as written; nz(line[1], close) on the first bar.
    * Every bar is an entry signal for its side (same-side ignored while held): stop-and-reverse (REVERSAL INTENDED);
      on a bar with both conditions the later short wins. No exits, no stops. FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR band around an SMA and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483027_sma_atr_line_rsi_always_in"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_len": [10, 20],
}
DEFAULT_PARAMS = {"atr_len": 10, "factor": 3.0, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["atr_len"])
    sma = c.rolling(n).mean()
    atr = _atr(bars_df, n)
    up = (sma + p["factor"] * atr).to_numpy()
    lw = (sma - p["factor"] * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        ref = cv[i] if np.isnan(prev) else prev           # nz(line[1], close)
        line[i] = lw[i] if cv[i] > ref else up[i]
        prev = line[i]
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    buy = cv > line
    sell = ~buy & ~np.isnan(line)
    short_e = sell & (rsi < p["rsi_ob"])
    long_e = buy & (rsi > p["rsi_os"]) & ~short_e
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(long_e, index=idx), false, pd.Series(short_e, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
