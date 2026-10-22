"""RSI 14 under 40 toggling a long, 30-minute bars, long only: on a bar with the RSI under 40 a flat position goes long and a held long closes, as written.
Port of FMZ strategy #441074 "基于RSI的长线量化策略Relative-Strength-Index-Long-term-Quant-Strategy" (RSI).

FMZ source id: 441074

Source
    https://www.fmz.com/strategy/441074 (PineScript v4, FMZ last modified 2024-02-05 13:51:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-166), RSI 14 on close (Pine's own formula); RSvalue 40; date window 2015-2022 (window() never used)
    rsi < 40 -> strategy.entry("BUY") then strategy.close("BUY") on the same bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position: on a flat bar the entry stands; on a bar where the long is
      held the entry does nothing and the close closes it. So a run of RSI-under-40 bars alternates long
      and flat, and a long left open is held to the next RSI-under-40 bar, as written. The date functions
      are never called. Long only. No sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level (entry and close in call order).
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

NAME = "fmz_441074_rsi_under_40_entry_close_toggle_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "rs_value": [40, 30],
}
DEFAULT_PARAMS = {"length": 14, "rs_value": 40}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["length"]))
    cond = (r < float(p["rs_value"])).to_numpy()
    m = len(cond)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0
    for i in range(m):
        if cond[i]:
            if held == 0 and i + 1 < m:
                le[i], held = True, 1
            elif held == 1:
                lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
