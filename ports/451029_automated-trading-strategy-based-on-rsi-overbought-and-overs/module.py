"""RSI 14 extremes held for one hour after the last signal, 1-hour bars: an RSI under 30 goes long, over 70 goes short; the first bar 60 minutes after the latest signal closes the position; reversing.
Port of FMZ strategy #451029 "Automated Trading Strategy Based on RSI Overbought and Oversold Levels" (Dougie Trades RSI Strategy V1).

FMZ source id: 451029

Source
    https://www.fmz.com/strategy/451029 (PineScript v5, FMZ last modified 2024-05-11 11:57:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-152), RSI 14, levels 30 / 70; exit after 60 minutes
    rsi < 30 -> entry Go Long, entryTime = time;  rsi > 70 -> entry Go Short, entryTime = time;  time - entryTime >= 60 minutes -> close Go Long, close Go Short, entryTime = na

Interpretation choices (Pine rules in SURVEY_README.md)
    * On 1-hour bars the timer runs out on the bar after the latest signal; every repeated signal
      restarts it, so a position is held while the RSI stays beyond its level and closes one bar
      after it leaves (filled at the next open). A close acts only on a held position. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the timer is a close-time test.
    2 generic: PASS, RSI extremes with a time exit.
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

NAME = "fmz_451029_rsi_extreme_one_hour_timer_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "exit_minutes": [60, 240],
}
DEFAULT_PARAMS = {"rsi_len": 14, "exit_minutes": 60, "os": 30.0, "ob": 70.0}


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
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    ts = bars_df.index.asi8 // 60_000_000_000             # bar open time in minutes
    lim = int(p["exit_minutes"])
    os_, ob = float(p["os"]), float(p["ob"])
    m = len(r)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, et = 0, None
    with np.errstate(invalid="ignore"):
        for i in range(m):
            new = pos
            if r[i] < os_:
                if new != 1:
                    le[i], new = True, 1
                et = ts[i]
            if r[i] > ob:
                if new != -1:
                    se[i], le[i], new = True, False, -1
                et = ts[i]
            if et is not None and ts[i] - et >= lim:
                if pos == 1 and new == 1:            # the closes act only on a held position
                    lx[i], new = True, 0
                elif pos == -1 and new == -1:
                    sx[i], new = True, 0
                et = None
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
