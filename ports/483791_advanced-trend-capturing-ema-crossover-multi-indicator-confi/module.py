"""EMA 9 / 21 crosses with SMA 200, RSI 50 and Bollinger-middle filters and a 1 ATR stop / 2 ATR target, 10-minute bars:
EMA 9 crossing above EMA 21 with the close above SMA 200, RSI 14 above 50 and the close above the 20-bar middle band
goes long; the mirror goes short.
Port of FMZ strategy #483791 "高级趋势捕捉型均线交叉多指标确认交易策略-Advanced-Trend-Capturing-EMA-Crossover-Multi-Indicator-Confirmation-Trading-Strategy" (Optimized BTC/USD Scalping).

FMZ source id: 483791

Source
    https://www.fmz.com/strategy/483791 (PineScript v5, FMZ last modified 2025-02-27 16:36:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 182-212), EMA 9 / 21, SMA 200, RSI 14, BB 20 x 2 middle, ATR 14, SL 1 / TP 2
    long = crossover(ema9, ema21) and close > sma200 and rsi > 50 and close > bb middle (short mirrored)
    entry + exit(limit = close +- 2 ATR, stop = close -+ 1 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop = tp_mult x ATR / close, shifted
      one bar inside stops() and re-based on the fill (house rule). A same-side signal while held re-places it: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "10min" from the backtest
      header. "BTC/USD" in the title is a label.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, RSI, the band middle and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483791_ema9_21_cross_filters_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.0, 1.5],
    "tp_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "sl_mult": 1.0, "tp_mult": 2.0}


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
    c = bars_df["close"]
    f, s = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    trend = c.rolling(200).mean()
    rsi = _rsi(c, 14)
    mid = c.rolling(20).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > trend) & (rsi > 50) & (c > mid)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < trend) & (rsi < 50) & (c < mid)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
