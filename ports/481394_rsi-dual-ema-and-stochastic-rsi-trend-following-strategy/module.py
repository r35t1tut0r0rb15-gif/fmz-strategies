"""EMA 9 / 21 golden crosses with the stochastic RSI K below 20 go long, death crosses with K above 80 go short, always
in, hourly bars.
Port of FMZ strategy #481394 "双均线与随机RSI趋势跟踪策略-Dual-EMA-and-Stochastic-RSI-Trend-Following-Strategy" (EMA 9/21 + Stoch RSI Strategy).

FMZ source id: 481394

Source
    https://www.fmz.com/strategy/481394 (PineScript v5, FMZ last modified 2025-02-10 16:56:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-160), EMA 9 / 21, RSI 14, stochastic 14, K smoothing 3 (80 / 20)
    crossover(ema9, ema21) and K < 20 -> entry long; crossunder and K > 80 -> entry short
    long and a short signal -> close long; short and a long signal -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes repeat the reversal of the entries (REVERSAL INTENDED); always in. Signal module, no stops.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and a stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_481394_ema9_21_cross_stoch_rsi_extreme_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "os": [20.0, 30.0],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "stoch_len": 14, "smooth": 3, "os": 20.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    rl, rh = rsi.rolling(n).min(), rsi.rolling(n).max()
    k = ((rsi - rl) / np.maximum(rh - rl, 1e-10) * 100).rolling(int(p["smooth"])).mean()
    ob = 100 - p["os"]
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (k < p["os"])).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (k > ob)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
