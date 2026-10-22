"""MACD cross-ups in an EMA 50 > 200 up-trend with RSI 14 under 70, hourly bars, long only, with no working exit: such a cross buys and the position is held. The 1.5 % stop armed only on "danger" bars is not ported (pending).
Port of FMZ strategy #481362 "Adaptive Trend Following Strategy with Dynamic Take Profit Using Multiple Technical Indicators" (BTC 15分钟动态止盈策略).

FMZ source id: 481362

Source
    https://www.fmz.com/strategy/481362 (PineScript v5, FMZ last modified 2025-02-10 14:59:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-172), EMA 50 / 200; MACD 12 / 26 / 9; RSI 14, 70; stop 1.5 % of strategy.position_avg_price, sent when the danger signal holds
    ema50 > ema200 and crossover(macd, signal) and rsi < 70 -> entry Buy;  long: exit(Buy, stop = avg x 0.985, when = danger)  (danger = down-trend or close < ema50 or MACD cross-down or RSI over 70 and falling 2 bars)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop exists only on bars where the danger condition holds (the deprecated when= argument), so it
      is armed and disarmed by that condition: a stop armed only by the exit condition is pending, with no
      exit (as #437800, mark trailing_stop_pending). The first long is therefore held to the end of the
      data in this port; repeat cross-ups while long are ignored. Long only. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the condition-armed stop described (pending).
    2 generic: PASS, MACD cross-ups in an EMA up-trend with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop percentage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_481362_macd_crossup_ema50_200_rsi70_long_no_exit"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [50, 20],
    "rsi_overbought": [70, 80],
}
DEFAULT_PARAMS = {"ema_short": 50, "rsi_overbought": 70, "ema_long": 200}


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
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    le = (es > el) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r < float(p["rsi_overbought"]))
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
