"""MACD zero crosses inside a rising EMA 5 / 14 / 34 / 55 stack with RSI above 50 go long with the stop at the EMA 34;
the falling-stack mirror closes the long (its own short exits at once), four-hour bars.
Port of FMZ strategy #482458 "Multi-EMA趋势追踪型RSI-MACD动量验证策略-Multi-EMA-Trend-Following-Strategy-with-RSI-MACD-Momentum-Validation" (EMA + MACD + RSI Strategy).

FMZ source id: 482458

Source
    https://www.fmz.com/strategy/482458 (PineScript v5, FMZ last modified 2025-02-18 15:13:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 92-138), EMA 5 / 14 / 34 / 55, RSI 14, MACD 12 / 26 / 9
    long = ema5 > ema14 > ema34 > ema55 and MACD crosses zero (either way) and rsi > 50 -> entry long
    short = the falling stack and a zero cross and rsi < 50 -> entry short
    every bar, both sides: exit(stop = ema34, limit = ema34 x 3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long's limit (3 x the EMA 34) is never reached (inert). The short's buy limit at 3 x the EMA 34 sits far
      above the market and fills at once, so every short ends at the next fill: a short signal only flattens a long
      (zero-length shorts are not emitted, as L2 #491035; the signal becomes the long's exit).
    * The long's stop is re-issued every bar at the current EMA 34 (a moving level): fixed at the entry as
      (close - ema34) / close of the signal bar, shifted one bar inside stops() and re-based on the fill; mark
      trailing_stop_pending. A signal with the close at or under the EMA 34 emits no entry (zero-length stop).
    * Long only in effect. Stop module: portfolio_kwargs {} (D4). FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, EMAs, MACD and RSI (the 3 x EMA limit is inert / immediate).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the stop via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (the short side only closes the long).

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482458_ema_stack_macd_zero_cross_ema34_stop_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_ema": [34, 55],
    "rsi_mid": [50.0, 55.0],
}
DEFAULT_PARAMS = {"stop_ema": 34, "rsi_mid": 50.0}


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


def _parts(bars_df, p):
    c = bars_df["close"]
    e5, e14, e34, e55 = (c.ewm(span=n, adjust=False).mean() for n in (5, 14, 34, 55))
    stop_line = c.ewm(span=int(p["stop_ema"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    zero_x = ((macd > 0) & (macd.shift(1) <= 0)) | ((macd < 0) & (macd.shift(1) >= 0))
    rsi = _rsi(c, 14)
    sl = (c - stop_line) / c
    long_e = (e5 > e14) & (e14 > e34) & (e34 > e55) & zero_x & (rsi > p["rsi_mid"]) & (sl > 0)
    short_c = (e5 < e14) & (e14 < e34) & (e34 < e55) & zero_x & (rsi < p["rsi_mid"])
    return long_e.astype(bool), short_c.astype(bool), sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_c, _ = _parts(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, (short_c & ~long_e).astype(bool), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _parts(bars_df, p)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
