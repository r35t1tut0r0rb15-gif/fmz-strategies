"""MACD crossings with RSI extremes near the 100-bar low or high, 1-minute bars: the MACD crossing over its signal with the RSI 14 under 30 and the close within 1 % of the 100-bar low goes long; the crossing
under with the RSI over 70 and the close within 1 % of the 100-bar high goes short; reversing.
Port of FMZ strategy #437801 "RSI和MACD结合支撑阻力的量化交易策略Quantitative-Trading-Strategy-Combining-RSI-MACD-and-Support-Resistance" (RSI_MACD_SR).

FMZ source id: 437801

Source
    https://www.fmz.com/strategy/437801 (PineScript v5, FMZ last modified 2024-01-05 16:24:58).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 142-168), RSI 14 (fixed), 70 / 30; MACD 12 / 26 / 9; support / resistance lowest(low, 100) / highest(high, 100); near = 1 % of the close
    long = crossover(macd, signal) and rsi < 30 and close - lowest(100) < 0.01 close -> entry Long;  short = crossunder(macd, signal) and rsi > 70 and highest(100) - close < 0.01 close -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 100-bar extremes include the current bar, as written. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings, RSI levels and rolling extremes.
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

NAME = "fmz_437801_macd_cross_rsi_near_sr"
FAMILY = "macd_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "near_frac": [0.01, 0.005],
    "fast": [12, 8],
}
DEFAULT_PARAMS = {"near_frac": 0.01, "fast": 12, "slow": 26, "signal": 9, "rsi_len": 14, "overbought": 70.0,
                  "oversold": 30.0, "sr_len": 100}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    k = int(p["sr_len"])
    support, resistance = lo.rolling(k).min(), h.rolling(k).max()
    near = float(p["near_frac"]) * c
    x_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    x_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    long_c = x_up & (r < float(p["oversold"])) & ((c - support) < near)
    short_c = x_dn & (r > float(p["overbought"])) & ((resistance - c) < near)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, false.copy()


def portfolio_kwargs(**params):
    return {}
