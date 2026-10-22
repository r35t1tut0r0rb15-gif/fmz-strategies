"""Bollinger, RSI and MACD extremes together, 4-hour bars: the close under the lower band (20, 2) with the RSI 14 under 30 and the MACD under its signal goes long, the mirror short; reversing.
Port of FMZ strategy #442639 "反转布林带RSI-MACD量化策略Reversal-Bollinger-Band-RSI-MACD-Quant-Strategy" (BBands + RSI + MACD Strategy).

FMZ source id: 442639

Source
    https://www.fmz.com/strategy/442639 (PineScript v4, FMZ last modified 2024-02-23 14:16:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-221), BB 20 / 2; RSI 14 (30 / 70); MACD 12 / 26 / 9; SMA 200 (plot only)
    close < lowerBB and rsi < 30 and macd < signal -> entry Buy;  close > upperBB and rsi > 70 and macd > signal -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are level tests, re-sent while they hold and refused while held. Pine's stdev is the
      population deviation. The SMA 200 only colours a plot. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band, RSI and MACD extremes.
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

NAME = "fmz_442639_bb_rsi_macd_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_bb": [20, 50],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"length_bb": 20, "oversold": 30, "mult_bb": 2.0, "rsi_len": 14, "fast": 12, "slow": 26, "signal": 9}


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
    n = int(p["length_bb"])
    basis = c.rolling(n).mean()
    dev = float(p["mult_bb"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    os_ = float(p["oversold"])
    le = (c < basis - dev) & (r < os_) & (macd < sig)
    se = (c > basis + dev) & (r > 100.0 - os_) & (macd > sig)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
