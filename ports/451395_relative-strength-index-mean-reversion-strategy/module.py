"""RSI 14 extremes on the far side of the SMA 20, 3-hour bars: an RSI under 30 below the SMA goes long, an RSI over 70 above it goes short; reversing (the stop / target close names an id that is never
entered and never acts).
Port of FMZ strategy #451395 "Relative Strength Index Mean Reversion Strategy" (Mean Reversion with Tight Stop Loss).

FMZ source id: 451395

Source
    https://www.fmz.com/strategy/451395 (PineScript v5, FMZ last modified 2024-05-14 16:01:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-132), RSI 14, levels 30 / 70; SMA 20; stop 0.5 %, target 1 % (close tests on the 'Exit' id)
    rsi < 30 and close < sma20 -> entry Buy;  rsi > 70 and close > sma20 -> entry Sell;  long and (close <= avg x 0.995 or close >= avg x 1.01) -> strategy.close('Exit')

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close's first argument is the entry id, and 'Exit' is never entered, so the stop /
      target close never acts: positions end at the opposite entry. Both entries are levels; a repeat
      on the held side is ignored. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest
      header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes beyond the SMA.
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

NAME = "fmz_451395_rsi_extreme_beyond_sma20_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "sma_len": [20, 50],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sma_len": 20, "os": 30.0, "ob": 70.0}


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
    r = _rsi(c, int(p["rsi_len"]))
    sma = c.rolling(int(p["sma_len"])).mean()
    le = (r < float(p["os"])) & (c < sma)
    se = (r > float(p["ob"])) & (c > sma)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
