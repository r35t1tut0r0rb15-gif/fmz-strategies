"""MACD turning up below zero in an EMA 50 > 200 up-trend, 15-minute bars, long only: such a bar buys; RSI 14 falling back through 70, or the EMA 50 dropping under the EMA 200, closes.
Port of FMZ strategy #478701 "多重指标趋势跟踪结合RSI超买超卖的量化交易策略-Multi-Indicator-Trend-Following-with-RSI-Overbought-Oversold-Quantitative-Trading-Strategy" (RSI ve EMA Tabanlı Alım-Satım Stratejisi).

FMZ source id: 478701

Source
    https://www.fmz.com/strategy/478701 (PineScript v5, FMZ last modified 2025-01-17 14:52:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-135), EMA 50 / 200; MACD 12 / 26 / 9; RSI 14, 70
    ema50 > ema200 and macd < 0 and macd > nz(macd[1]) and nz(macd[1]) < nz(macd[2]) -> entry Buy;  rsi[1] > 70 and rsi <= 70 -> close Buy;  ema50 < ema200 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop follows the call order: an entry from flat stands even when a close is sent on its bar, and a
      close on a bar with a repeat buy while long ends the trade (as #472251). Long only. No sizing code.
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD turns below zero in an EMA up-trend with RSI and trend exits.
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

NAME = "fmz_478701_macd_turn_below_zero_ema50_200_rsi70_exit_long"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [50, 20],
    "rsi_exit": [70, 60],
}
DEFAULT_PARAMS = {"ema_short": 50, "rsi_exit": 70, "ema_long": 200}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    m1, m2 = macd.shift(1).fillna(0.0), macd.shift(2).fillna(0.0)
    buy = ((es > el) & (macd < 0) & (macd > m1) & (m1 < m2)).to_numpy()
    r = _rsi(c, 14)
    lv = float(p["rsi_exit"])
    out = (((r.shift(1) > lv) & (r <= lv)) | (es < el)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if buy[i] and pos == 0:
            le[i], nxt = True, 1
        if out[i] and pos == 1:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
