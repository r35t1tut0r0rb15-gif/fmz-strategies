"""Faded Bollinger breakouts, 2-hour bars: the previous close having crossed over the upper band (20 / 2), with the RSI 14 over 50 and the MACD over its signal, goes SHORT; the previous close having crossed under the lower band with the RSI under 50 and the MACD under its signal goes LONG; reversing.
Port of FMZ strategy #451727 "Reverse Volatility Breakout Strategy" (Volatility Breakout Strategy (Reversed)).

FMZ source id: 451727

Source
    https://www.fmz.com/strategy/451727 (PineScript v5, FMZ last modified 2024-05-17 15:18:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-132), Bollinger 20 / 2; RSI 14; MACD 12 / 26 / 9; ATR 14 (unused)
    crossover(close[1], upper[1]) and rsi > 50 and macd > signal -> entry Sell (short);  crossunder(close[1], lower[1]) and rsi < 50 and macd < signal -> entry Buy (long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crossing is of the previous bar (close[1] against upper[1], one bar later than the signal
      bar's own close), the RSI and MACD tests are on the current bar. The two entries cannot meet on
      one bar (RSI over against under 50). There is no exit: positions end at the opposite entry. The
      ATR is computed but unused. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest
      header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, faded band breakouts with RSI / MACD agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451727_faded_bollinger_breakout_rsi_macd_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [20, 50],
    "bb_mult": [2.0, 2.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "rsi_len": 14}


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
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    c1, c2 = c.shift(1), c.shift(2)
    up_x = (c1 > upper.shift(1)) & (c2 <= upper.shift(2))
    dn_x = (c1 < lower.shift(1)) & (c2 >= lower.shift(2))
    se = up_x & (r > 50) & (macd > sig)
    le = dn_x & (r < 50) & (macd < sig)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
