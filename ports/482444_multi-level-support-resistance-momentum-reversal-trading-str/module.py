"""RSI 14 below 30 with the close above the 61.8 % retracement of the all-time range of up-closes goes long; RSI above
70 with the close below the 38.2 % level closes it, long only, hourly bars.
Port of FMZ strategy #482444 "多重支撑阻力位叠加动量反转交易策略-Multi-Level-Support-Resistance-Momentum-Reversal-Trading-Strategy" (Fibonacci Retracement + Pivot Points + RSI Strategy).

FMZ source id: 482444

Source
    https://www.fmz.com/strategy/482444 (PineScript v5, FMZ last modified 2025-02-18 14:49:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 122-177), RSI 14 (70 / 30)
    on every up-close: fib_low = min(fib_low, close), fib_high = max(fib_high, close) (var, from the first bar)
    fib_38 / 50 / 61 = fib_high - (fib_high - fib_low) x 0.382 / 0.5 / 0.618
    buy = (close > fib_38 or close > fib_50 or close > fib_61) and rsi < 30 -> entry long
    sell = (close < fib_38 or close < fib_50 or close < fib_61) and rsi > 70 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are expanding extremes of up-closes since the first bar (past values only); they depend on where
      the data starts, as in the source. The "or" tests reduce to close > fib_61 and close < fib_38.
    * The pivots feed only drawings.
    * The close is written after the entry: it acts on the position held at the bar's start and never undoes an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Long only. Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, retracement fractions of a range and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 20 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482444_rsi_extreme_fib_range_levels_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ob": 70.0, "os": 30.0}


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
    cv = c.to_numpy(dtype=float)
    up_close = (c.diff() > 0).to_numpy()
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lo_f = hi_f = np.nan
    pos = 0
    for i in range(m):
        if up_close[i]:
            lo_f = cv[i] if np.isnan(lo_f) else min(lo_f, cv[i])
            hi_f = cv[i] if np.isnan(hi_f) else max(hi_f, cv[i])
        f38 = hi_f - (hi_f - lo_f) * 0.382
        f61 = hi_f - (hi_f - lo_f) * 0.618
        start = pos
        if cv[i] > f61 and rsi[i] < p["os"] and pos != 1:
            le[i], pos = True, 1
        if cv[i] < f38 and rsi[i] > p["ob"] and start == 1 and pos == 1:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
