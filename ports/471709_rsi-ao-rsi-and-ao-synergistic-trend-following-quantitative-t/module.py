"""Buying a negative Awesome Oscillator after an RSI over 50, 1-hour bars, long only: an AO (SMA 5 - SMA 34 of hl2) under zero with the previous bar's RSI 14 over 50 buys, with a 2 % target and 1 % stop from the fill.
Port of FMZ strategy #471709 "RSI与AO协同趋势追踪型量化交易策略-RSI-and-AO-Synergistic-Trend-Following-Quantitative-Trading-Strategy" (BUY Only - RSI Crossing 50 + AO Negative).

FMZ source id: 471709

Source
    https://www.fmz.com/strategy/471709 (PineScript v5, FMZ last modified 2024-11-12 16:05:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-218), AO 5 / 34 of hl2; RSI 14 of close; target 2 %, stop 1 % of the average price
    ao < 0 and rsi[1] > 50 -> entry Long;  while long: exit(stop = avg x 0.99, limit = avg x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the average (fill) price and is sent every bar while held: ported active
      from the fill bar (#440797) as the fixed fractions 0.02 / 0.01 of the fill. The entry test is a
      state: repeated entries while held do nothing. The AO and RSI crossing markers are drawing only.
      Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, negative AO after RSI strength, percent bracket.
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

NAME = "fmz_471709_negative_ao_after_rsi_over_50_pct_bracket_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.02, 0.04],
    "sl_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"tp_pct": 0.02, "sl_pct": 0.01, "rsi_len": 14, "ao_short": 5, "ao_long": 34}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    ao = hl2.rolling(int(p["ao_short"])).mean() - hl2.rolling(int(p["ao_long"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (ao < 0) & (r.shift(1) > 50)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
