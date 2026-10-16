"""Two-RSI momentum, long only, hourly bars: RSI 2 or RSI 14 crossing up through 50 with both above 50 goes long; RSI 7
or RSI 50 crossing down through 50 with both below 50 closes it.
Port of FMZ strategy #429504 "TAM日内RSI交易策略TAM-Intraday-RSI-Trading-Strategy" (TAM - RSI Strategy).

FMZ source id: 429504

Source
    https://www.fmz.com/strategy/429504 (PineScript v5, FMZ last modified 2023-10-17 16:58:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 199-230), buy RSI 2 / 14 vs 50, close RSI 7 / 50 vs 50
    buy = (crossover(rsi2, 50) or crossover(rsi14, 50)) and rsi2 > 50 and rsi14 > 50 -> entry long
    close = (crossunder(rsi7, 50) or crossunder(rsi50, 50)) and rsi7 < 50 and rsi50 < 50 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date filter (from 2020) is dropped (inTradeWindow is true).
    * Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels only.
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

NAME = "fmz_429504_two_rsi_momentum_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_len2": [14, 21],
    "close_len2": [50, 30],
}
DEFAULT_PARAMS = {"buy_len1": 2, "buy_len2": 14, "buy_value": 50, "close_len1": 7, "close_len2": 50,
                  "close_value": 50}


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
    c = bars_df["close"]
    b1, b2 = _rsi(c, int(p["buy_len1"])), _rsi(c, int(p["buy_len2"]))
    c1, c2 = _rsi(c, int(p["close_len1"])), _rsi(c, int(p["close_len2"]))
    bv, cv = float(p["buy_value"]), float(p["close_value"])
    xo = lambda r, v: (r > v) & (r.shift(1) <= v)  # noqa: E731
    xu = lambda r, v: (r < v) & (r.shift(1) >= v)  # noqa: E731
    long_e = ((xo(b1, bv) | xo(b2, bv)) & (b1 > bv) & (b2 > bv)).astype(bool)
    long_x = ((xu(c1, cv) | xu(c2, cv)) & (c1 < cv) & (c2 < cv)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
