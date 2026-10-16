"""RSI dips and rips around the EMA 162, 1-minute bars: above the EMA with RSI 14 under 35 goes long, below the EMA
with RSI 14 above 35 goes short (the exits have no levels and never act).
Port of FMZ strategy #429468 "Gold Silver 30m Trend Following Breakout Strategy" (My Strategy).

FMZ source id: 429468

Source
    https://www.fmz.com/strategy/429468 (PineScript v2, FMZ last modified 2023-10-17 14:11:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 247-271), RSI 14, OB 65 / OS 35, EMA 162 (the Bollinger band is computed, unused)
    close > ema(close,162) and rsi < 35 -> entry long; close < ema(close,162) and rsi > 35 -> entry short (as written: OS on both)
    strategy.exit(id, when = ...) with no stop, limit, profit, loss or trail: inert

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit with only `when` places no order: the positions change only by the opposite entry.
      The short test uses the oversold level 35, as written. The Bollinger band is unused.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header (the title's
      "30m" is not the header's period).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and a moving-average side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() pyramiding 1 and commission stored.
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

NAME = "fmz_429468_rsi_dip_rip_ema162"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "ema_length": [162, 100],
}
DEFAULT_PARAMS = {"rsi_length": 14, "ema_length": 162, "oversold": 35}


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
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    long_e = ((c > ema) & (r < p["oversold"])).astype(bool)
    short_e = ((c < ema) & (r > p["oversold"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
