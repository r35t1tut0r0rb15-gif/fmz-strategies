"""Rebounds after a run of down closes, 2-hour bars, long only: two up closes after three or more down closes (ending two bars back) go long; a close under the lowest of the last three signal closes, or more
than 2 ATR(7) under the bar's high, closes.
Port of FMZ strategy #443643 "连续K线反转突破策略Consecutive-Candlestick-Reversal-Breakout-Strategy" (Bottom Out Strategy).

FMZ source id: 443643

Source
    https://www.fmz.com/strategy/443643 (PineScript v5, FMZ last modified 2024-03-05 16:07:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-154), consecutive up 2, down 3; ATR 7 x 2; dates (date() true)
    ups / dns = counts of consecutive higher / lower closes;  dns[2] >= 3 and ups >= 2 and not active -> entry ConsDnLong, active, stop_loss = min(close, close[1], close[2])
    active and (close < stop_loss or close < high - 2 atr(7)) -> close, active = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The active flag is set on the signal bar and cleared by the exit test, which can fire on the
      signal bar itself (the close under its high by 2 ATR) before the entry fills; such a close acts
      on no open position, as written, and the flag stays off until the next signal (a signal while the
      position is open is refused). The tests run at the bar close. Long only. No sizing code. FREQ =
      "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close-run reversal with close-tested exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG443643 (2 members, best partner #444031, Jaccard 0.925); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443643_down_run_rebound_close_stop_long"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars_up": [2, 3],
    "bars_down": [3, 5],
}
DEFAULT_PARAMS = {"bars_up": 2, "bars_down": 3, "atr_len": 7, "atr_mult": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ups, dns = np.zeros(m), np.zeros(m)
    for i in range(1, m):
        ups[i] = ups[i - 1] + 1 if cv[i] > cv[i - 1] else 0
        dns[i] = dns[i - 1] + 1 if cv[i] < cv[i - 1] else 0
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    lvl = (h - float(p["atr_mult"]) * _rma(tr, int(p["atr_len"]))).to_numpy()
    nu, nd = int(p["bars_up"]), int(p["bars_down"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, active, stop = False, False, np.nan
    for i in range(m):
        if i >= 2 and dns[i - 2] >= nd and ups[i] >= nu and not active:
            if not held:
                le[i] = True
            active = True
            stop = min(cv[i], cv[i - 1], cv[i - 2])
        if active and (cv[i] < (0.0 if np.isnan(stop) else stop) or cv[i] < lvl[i]):
            if held:
                lx[i] = True
            active = False
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
