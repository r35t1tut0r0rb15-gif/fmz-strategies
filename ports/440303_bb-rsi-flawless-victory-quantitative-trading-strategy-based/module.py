"""Bollinger dips with RSI, 1-hour bars, long only (version 1): the close under the lower Bollinger band (20, 1 sd) with the RSI 14 above 42 goes long; the close over the upper band with the RSI above 70
closes.
Port of FMZ strategy #440303 "双BB指标RSI量化交易策略Flawless-Victory-Quantitative-Trading-Strategy-Based-on-Double-BB-Indicators-and-RSI" (Flawless Victory Strategy).

FMZ source id: 440303

Source
    https://www.fmz.com/strategy/440303 (PineScript v4, FMZ last modified 2024-01-29 10:33:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-153), version 1 on, version 2 off; BB 20 / 1.0 and 17 / 1.0; RSI 14; limits 42 / 70 (v1), 42 / 76 (v2); v2 stop 6.604 %, target 2.328 %
    Buy = rsi > 42 and close < lower(20, 1);  Sell = rsi > 70 and close > upper(20, 1);  v1: entry Long when Buy, close Long when Sell
    v2 (off): the same on BB 17 with 42 / 76, plus strategy.exit(stop = avg price x (1 - 6.604 %), limit = avg price x (1 + 2.328 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Version 1 is the default and is ported; version 2 (off) is not. Pine's stdev is the population
      deviation. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and RSI.
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

NAME = "fmz_440303_flawless_victory_bb_rsi_v1"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_ll": [42, 30],
    "rsi_ul": [70, 76],
}
DEFAULT_PARAMS = {"rsi_ll": 42, "rsi_ul": 70, "bb_len": 20, "bb_mult": 1.0, "rsi_len": 14}


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
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    buy = (r > float(p["rsi_ll"])) & (c < basis - dev)
    sell = (r > float(p["rsi_ul"])) & (c > basis + dev)
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
