"""RSI 2 dips, long only, 1-hour bars: an RSI 2 under 15 goes long; a close above the previous bar's high closes.
Port of FMZ strategy #439989 "Dual Indicators Breakthrough Strategy" (Hobbiecode - RSI + Close previous day).

FMZ source id: 439989

Source
    https://www.fmz.com/strategy/439989 (PineScript v5, FMZ last modified 2024-01-25 15:39:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-154), RSI 2, level 15
    if rsi(close, 2) < 15: entry Buy;  if long and close > highest(high[1], 1): close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(high[1], 1) is the previous bar's high. The entry and the close act on the position held
      at the bar close: from flat the entry opens; a long meeting both closes. Long only. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level and a prior-high break.
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

NAME = "fmz_439989_hobbiecode_rsi2_prior_high_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [2, 3],
    "rsi_lower": [15, 10],
}
DEFAULT_PARAMS = {"rsi_period": 2, "rsi_lower": 15}


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
    c = bars_df["close"]
    le = (_rsi(c, int(p["rsi_period"])) < float(p["rsi_lower"])).to_numpy()
    lx = (c > bars_df["high"].shift(1)).to_numpy()
    m = len(c)
    o_le, o_lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1:
            if lx[i]:
                o_lx[i], pos = True, 0
        elif le[i]:
            o_le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(o_le, index=ix), pd.Series(o_lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
