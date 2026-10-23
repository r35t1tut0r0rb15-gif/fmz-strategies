"""Hourly bars, long only: the EMA 10 crossing over the EMA 20 on the same bar as a MACD cross-up, above the EMA 50 / 100 / 200 with RSI 14 over 55, above the 50-bar mid-range and on volume over 1.5 x its 20-bar average, goes long; the mirror set-up closes it; a 2 % stop under each bar's close, re-sent every bar, is followed in the signals.
Port of FMZ strategy #488128 "Multi Indicator Trend Confirmation High Profit Quantitative Trading Strategy" (Solana Max Profit Strategy).

FMZ source id: 488128

Source
    https://www.fmz.com/strategy/488128 (PineScript v5, FMZ last modified 2025-03-25 11:36:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 184-235), EMA 10 / 20 / 50 / 100 / 200; RSI 14; MACD 12 / 26 / 9; volume SMA 20 x 1.5; 50-bar mid; stop close x 0.98, target close x 2 (every bar); 30 % of equity
    long_condition = crossover(ema10, ema20) and close above EMA 50 / 100 / 200 and rsi > 55 and trend == 1 and crossover(macd, signal) and strong_volume -> entry Buy;  short_condition (mirror) -> close Buy
    every bar: exit("Take Profit", "Buy", limit = close x 2.0, stop = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is re-sent every bar from that bar's close (including the signal bar, for the pending
      entry), so its stop moves both ways; the signals follow it: a bar whose low reaches 0.98 x the
      previous close closes the trade at the next open (mark trailing_stop_pending); the 100 % target is
      out of reach in practice. A buy and the mirrored close never meet on one bar. The title names
      Solana; the header is BNB_USDT. Long only. 30 % of equity is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent stop followed in the signals.
    2 generic: PASS, aligned EMA and MACD crossings in a strong uptrend on volume.
    3 crypto-exchange-only: no (exchange pair in the header only (Solana named in the title)).
    4 signals only: 30 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488128_ema_macd_cross_trend_stack_volume_rolling_stop_1h_long_only"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl": [0.02, 0.03],
    "tp": [1.0, 0.1],
}
DEFAULT_PARAMS = {"sl": 0.02, "tp": 1.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    e10, e20, e50, e100, e200 = (c.ewm(span=n, adjust=False).mean() for n in (10, 20, 50, 100, 200))
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    strong = v > v.rolling(20).mean() * 1.5
    mid = (h.rolling(50).max() + lo.rolling(50).min()) / 2
    up = c > mid
    buy = ((e10 > e20) & (e10.shift(1) <= e20.shift(1)) & (c > e50) & (c > e100) & (c > e200) & (r > 55) & up
           & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & strong).to_numpy()
    sell = ((e10 < e20) & (e10.shift(1) >= e20.shift(1)) & (c < e50) & (c < e100) & (c < e200) & (r < 45) & ~up
            & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & strong).to_numpy()
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held == 1 and (ln[i] <= cn[i - 1] * (1 - sl) or hn[i] >= cn[i - 1] * (1 + tp)):
            held = 0                       # the exit sent at the previous close is touched
        new = held
        if buy[i] and held == 0:
            new = 1
        elif sell[i] and held == 1:
            new = 0
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            else:
                lx[i] = True
            vpos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
