"""Stochastic RSI above 35 in a breakout regime, long only, 3-hour bars: K above 35 with the close above the 30-bar
highest EMA 6 of highs goes long; K crossing down through 35 closes it.
Port of FMZ strategy #429471 "Bull Trend Riding Strategy Based on Stochastic RSI with Special Rules for Heavy Bullish Bias" (Filtered Stoch).

FMZ source id: 429471

Source
    https://www.fmz.com/strategy/429471 (PineScript v5, FMZ last modified 2023-10-17 14:31:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 195-228), EMA 6 of high, Donchian 30, stoch-RSI 14 / 14 / 7 / 4, lower band 35
    ema = highest(ema(high, 6), 30); k = clamp(sma(stoch(rsi14, rsi14, rsi14, 14), 7), 0, 100)
    k > 35 and close > ema -> entry long; crossunder(k, 35) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * D is drawn only. The stochastic of the RSI includes the current bar.
    * Long only. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a price-vs-line test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
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

NAME = "fmz_429471_filtered_stoch_rsi_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_donchian_len": [30, 50],
    "lowerband": [35, 20],
}
DEFAULT_PARAMS = {"filter_ema_len": 6, "ema_donchian_len": 30, "smooth_k": 7, "rsi_length": 14,
                  "stoch_length": 14, "lowerband": 35}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c = bars_df["high"], bars_df["close"]
    line = h.ewm(span=int(p["filter_ema_len"]), adjust=False).mean().rolling(int(p["ema_donchian_len"])).max()
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["stoch_length"])
    ll, hh = r.rolling(n).min(), r.rolling(n).max()
    k = (100 * (r - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean().clip(0, 100)
    lb = float(p["lowerband"])
    long_e = ((k > lb) & (c > line)).astype(bool)
    long_x = ((k < lb) & (k.shift(1) >= lb)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
