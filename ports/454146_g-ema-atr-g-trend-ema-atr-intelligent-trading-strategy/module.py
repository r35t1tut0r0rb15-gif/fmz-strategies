"""G-Channel trend (length 100) against the EMA 50, 2-hour bars: a bullish channel trend with the close under the EMA 50 is long, a bearish one with the close over it is short; reversing. The ATR bracket re-sent from every signal bar's close is not ported (pending).
Port of FMZ strategy #454146 "G趋势EMA-ATR智能交易策略G-Trend-EMA-ATR-Intelligent-Trading-Strategy" (G-Trend EMA ATR Strategy).

FMZ source id: 454146

Source
    https://www.fmz.com/strategy/454146 (PineScript v4, FMZ last modified 2024-06-14 15:35:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-160), G-Channel length 100; EMA 50; ATR 14; stop 2 ATR, target 4 ATR from the signal close (every signal bar)
    a = max(close, a[1]) - (a[1] - b[1]) / 100;  b = min(close, b[1]) + (a[1] - b[1]) / 100;  crossup: b[1] < close[1] and b > close;  crossdn: a[1] < close[1] and a > close
    bullish = barssince(crossdn) <= barssince(crossup);  bullish and close < ema50 -> entry Buy, exit(stop = close - 2 atr, limit = close + 4 atr);  not bullish and close > ema50 -> entry Sell (mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel starts from 0 (nz) as written; its 'cross' tests are the channel lines crossing the
      close as written (b moving over the close, a moving over the close). Both entries are states, and
      the bracket is re-sent on every bar the condition holds, from that bar's close, so its levels move
      while the trade is on; stops() cannot express this: it is not ported and the module gets the mark
      trailing_stop_pending (as #438034); positions end at the opposite entry. REVERSAL INTENDED. No
      sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending (mark).
    2 generic: PASS, channel trend against the EMA.
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

NAME = "fmz_454146_g_channel_trend_vs_ema50_state_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"length": 100, "ema_len": 50}


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


def _barssince(ev):
    out = np.full(len(ev), np.nan)
    last = -1
    for i in range(len(ev)):
        if ev[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = float(p["length"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    a, b = np.full(m, np.nan), np.full(m, np.nan)
    pa = pb = 0.0
    for i in range(m):
        a[i] = max(cv[i], pa) - (pa - pb) / n
        b[i] = min(cv[i], pb) + (pa - pb) / n
        pa, pb = a[i], b[i]
    a1, b1 = np.concatenate(([np.nan], a[:-1])), np.concatenate(([np.nan], b[:-1]))
    c1 = np.concatenate(([np.nan], cv[:-1]))
    with np.errstate(invalid="ignore"):
        cross_up = (b1 < c1) & (b > cv)
        cross_dn = (a1 < c1) & (a > cv)
        bull = _barssince(cross_dn) <= _barssince(cross_up)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    le = bull & (cv < ema)
    se = ~bull & (cv > ema)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
