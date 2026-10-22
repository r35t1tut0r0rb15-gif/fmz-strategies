"""EMA, MACD and RSI agreement, 1-hour bars: the close above the EMA 20 with the MACD above its signal and the RSI above its EMA 20 goes long, all three reversed goes short; reversing.
Port of FMZ strategy #440312 "Triple Indicator Collision Strategy" (MACD_RSI strategy).

FMZ source id: 440312

Source
    https://www.fmz.com/strategy/440312 (PineScript v4, FMZ last modified 2024-01-29 11:24:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-173), EMA 20; MACD 12 / 26 / signal EMA 20; RSI 14 with an EMA 20 signal
    longCondition = close > ema20 and macd > ema(macd, 20) and rsi > ema(rsi, 20) -> entry Buy;  shortCondition = all three below -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels: an entry while already in that direction does nothing. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA, MACD and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440312_ema_macd_rsi_agreement"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
    "signal_len": [20, 9],
}
DEFAULT_PARAMS = {"ema_len": 20, "signal_len": 20, "fast": 12, "slow": 26, "rsi_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sl = int(p["signal_len"])
    ms = macd.ewm(span=sl, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    rs = r.ewm(span=sl, adjust=False).mean()
    up = (c > e) & (macd > ms) & (r > rs)
    dn = (c < e) & (macd < ms) & (r < rs)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
