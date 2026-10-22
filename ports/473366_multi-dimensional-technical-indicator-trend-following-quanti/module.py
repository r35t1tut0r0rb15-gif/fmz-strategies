"""Any-of-three bias, 4-hour bars: RSI 14 under 30, MACD 12 / 26 / 9 over its signal or EMA 20 over EMA 50 sends a long; RSI over 70, MACD under its signal or EMA 20 under EMA 50 sends a short, and the short (written later) wins when both are sent; reversing. The 1 % stop re-sent from the close once a long is 5 % in profit is not ported (pending).
Port of FMZ strategy #473366 "Multi Dimensional Technical Indicator Trend Following Quantitative Strategy" (Quantico Bot MILLIONARIO).

FMZ source id: 473366

Source
    https://www.fmz.com/strategy/473366 (PineScript v5, FMZ last modified 2024-11-29 15:33:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-162), RSI 14, MACD 12 / 26 / 9, EMA 20 / 50, all switched on; trailing trigger 5 %, stop close x 0.99; TP / SL inputs shown in labels only
    compra = rsi < 30 or macd > signal or ema20 > ema50 -> entry Compra;  venda = rsi > 70 or macd < signal or ema20 < ema50 -> entry Venda;  long and close >= avg x 1.05 -> exit(stop = close x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries are sent every bar their tests hold; when both hold, the later call (the short)
      wins (#437773), so longs need every short test false. The 1 % stop is re-sent on each bar from
      that bar's close once the long is 5 % up: a level re-set every bar is not ported (as #438034,
      mark trailing_stop_pending). The take-profit and stop-loss inputs and strategy.netprofit only feed
      labels. REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, any-of-three indicator bias; profit-armed stop described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital and risk inputs shown only.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473366_rsi_macd_ema_any_of_three_bias_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
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


def simulate(bars_df, **params):
    c = bars_df["close"]
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    buy = (r < 30) | (macd > sig) | (e20 > e50)
    sell = (r > 70) | (macd < sig) | (e20 < e50)
    se = sell
    le = buy & ~sell                             # the later short entry wins a bar with both
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
