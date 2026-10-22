"""EMA 50 / 100 bands with RSI 14, hourly bars, long only: in a green band (EMA 50 above 100) entered by a crossing, RSI over 70 buys; the band turning red closes.
Port of FMZ strategy #481393 "双均线RSI动量突破交易策略-Dual-EMA-RSI-Momentum-Breakout-Trading-Strategy" (IME-Bands with RSI Strategy).

FMZ source id: 481393

Source
    https://www.fmz.com/strategy/481393 (PineScript v5, FMZ last modified 2025-02-10 16:54:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-162), EMA 50 / 100; RSI 14, 70; stop at the EMA 100 of the crossing bar (reset on entry)
    green = ema50 > ema100;  green and not green[1] -> confirmed := true, stop := ema100;  not green -> confirmed := false;  confirmed and rsi > 70 and green -> entry Buy, stop := na;  red -> close Buy;  long and stop -> exit(stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The confirmation flag needs a crossing into the green band, so the band in progress at the start of
      the data does not count. The stop level is cleared on the entry bar and only set again on a new
      crossing, which cannot come while long (the red band closes first), so the stop exit never acts, as
      written. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA band trend with an RSI breakout entry.
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

NAME = "fmz_481393_ema50_100_green_band_rsi70_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_small": [50, 20],
    "rsi_level": [70, 60],
}
DEFAULT_PARAMS = {"ema_small": 50, "rsi_level": 70, "ema_big": 100, "rsi_length": 14}


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
    es = c.ewm(span=int(p["ema_small"]), adjust=False).mean()
    eb = c.ewm(span=int(p["ema_big"]), adjust=False).mean()
    green = (es > eb).to_numpy()
    red = (es < eb).to_numpy()
    m = len(green)
    conf = np.zeros(m, dtype=bool)
    st = False
    for i in range(m):
        if i > 0 and green[i] and not green[i - 1]:
            st = True
        if not green[i]:
            st = False
        conf[i] = st
    r = _rsi(c, int(p["rsi_length"]))
    ix = c.index
    le = pd.Series(conf & green, index=ix) & (r > float(p["rsi_level"]))
    false = pd.Series(False, index=ix)
    return le, pd.Series(red, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
