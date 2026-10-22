"""Bollinger 20 / 2 extremes with MACD and RSI 14 confirmation, 1-minute bars: a close under the lower band with the MACD over its signal and the RSI under 30 goes long, the mirror goes short; reversing.
Port of FMZ strategy #458176 "Multi Indicator Dynamic Volatility Alert Trading System" (Bollinger Bands with MACD and RSI Strategy).

FMZ source id: 458176

Source
    https://www.fmz.com/strategy/458176 (PineScript v5, FMZ last modified 2024-07-30 15:57:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-217), BB 20, 2 sd; MACD 12 / 26 / 9; RSI 14, levels 30 / 70
    close < lower and macd > signal and rsi < 30 -> entry Buy;  close > upper and macd < signal and rsi > 70 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tests are states: repeated entries while held do nothing. There is no exit: positions end at
      the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band extremes with MACD and RSI confirmation.
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

NAME = "fmz_458176_bb20_extreme_macd_rsi_confirm_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "fast": 12, "slow": 26, "signal": 9, "rsi_len": 14}


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
    n, k = int(p["length"]), float(p["mult"])
    basis = c.rolling(n).mean()
    dev = k * c.rolling(n).std(ddof=0)
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (c < basis - dev) & (macd > sig) & (r < 30)
    se = (c > basis + dev) & (macd < sig) & (r > 70)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
