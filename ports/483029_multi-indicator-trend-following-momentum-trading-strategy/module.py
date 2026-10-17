"""MACD crosses on the SMA 200 side after a recent EMA 50 pullback, with a 40 % stop and a 150 % target as written,
1-hour bars: above SMA 200, a MACD cross up with RSI above 50 and the close below EMA 50 within the last 5 bars goes
long; the mirror goes short.
Port of FMZ strategy #483029 "多重指标趋势跟踪动量交易策略-Multi-Indicator-Trend-Following-Momentum-Trading-Strategy" (Trend-Following Momentum Strategy).

FMZ source id: 483029

Source
    https://www.fmz.com/strategy/483029 (PineScript v6, FMZ last modified 2025-02-21 10:06:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 97-132), SMA 200, EMA 50, RSI 14, MACD 12 / 26 / 9, RR 1.5, trail 1 % on
    long = close > sma200 and crossover(macd, signal) and rsi > 50 and barssince(close < ema50) < 5 (short mirrored)
    exit(limit = close x (1 + 1.5), stop = close x (1 - 1 / 2.5), trail_price = close x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target and stop are as written: +150 % and -40 % of the signal close (the author multiplied the price by the
      ratio itself), fractions re-based on the fill (house rule); shorts mirrored (-150 % target, +40 % stop).
    * trail_price without trail_offset sets no trailing stop: inert (as trail_points without offset).
    * A same-side signal while held re-places the bracket at the same fractions from the new close: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, RSI, MACD and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483029_macd_cross_pullback_trend_wide_bracket"
FAMILY = "macd"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [50, 20],
    "pullback_bars": [5, 10],
}
DEFAULT_PARAMS = {"ma_len": 200, "ema_len": 50, "rsi_len": 14, "rr": 1.5, "pullback_bars": 5}


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


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = None
    for i, v in enumerate(cond):
        if v:
            last = i
        if last is not None:
            out[i] = i - last
    return out


def _signals(bars_df, p):
    c = bars_df["close"]
    ma = c.rolling(int(p["ma_len"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    k = int(p["pullback_bars"])
    pb_l = _barssince((c < ema).to_numpy())
    pb_s = _barssince((c > ema).to_numpy())
    pull_l = np.where(np.isnan(pb_l), False, pb_l < k)
    pull_s = np.where(np.isnan(pb_s), False, pb_s < k)
    long_e = ((c > ma) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (rsi > 50)).to_numpy() & pull_l
    short_e = ((c < ma) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (rsi < 50)).to_numpy() & pull_s
    return pd.Series(long_e, index=c.index), pd.Series(short_e, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rr = float(p["rr"])
    return {"sl_stop": 1 / (1 + rr), "tp_stop": rr}


def portfolio_kwargs(**params):
    return {}
