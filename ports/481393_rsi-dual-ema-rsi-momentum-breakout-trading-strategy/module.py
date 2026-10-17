"""While the EMA 50 is above the EMA 100, RSI 14 above 70 goes long; the EMA 50 under the EMA 100 closes it, long
only, hourly bars.
Port of FMZ strategy #481393 "双均线RSI动量突破交易策略-Dual-EMA-RSI-Momentum-Breakout-Trading-Strategy" (IME-Bands with RSI Strategy).

FMZ source id: 481393

Source
    https://www.fmz.com/strategy/481393 (PineScript v5, FMZ last modified 2025-02-10 16:54:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-154), EMA 50 / 100, RSI 14 (70)
    green = ema50 > ema100; confirmed := true on the first green bar, false on a non-green bar
    confirmed and green and rsi > 70 -> entry long; ema50 < ema100 -> close long
    stop = ema100 at the green crossover, reset to na on entry; exit(stop) while long and the stop is set

Interpretation choices (Pine rules in SURVEY_README.md)
    * "confirmed" equals "green" (set on the green transition, cleared on any non-green bar).
    * The stop is reset to na on every entry and set again only on a new green transition, which needs a red bar that
      has already closed the trade: it never acts (inert).
    * Entries and closes cannot fall on one bar. Long only. Signal module, no stops. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and an RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481393_ema50_100_green_rsi70_momentum_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_ob": [70.0, 60.0],
    "slow": [100, 200],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 100, "rsi_len": 14, "rsi_ob": 70.0}


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
    long_e = ((f > s) & (rsi > p["rsi_ob"])).astype(bool)
    long_x = (f < s).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
