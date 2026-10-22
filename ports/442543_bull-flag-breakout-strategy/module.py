"""Bull flags, 1-hour bars, long only: a flagpole (one to three rising closes covering more than 3 ATR(10) of the prior bar) followed by three bars whose open and close stay in the top third of the pole goes
long; six bars after the latest flag the long is closed.
Port of FMZ strategy #442543 "Bull Flag Breakout Strategy" (Bull Flag v1.00).

FMZ source id: 442543

Source
    https://www.fmz.com/strategy/442543 (PineScript v4, FMZ last modified 2024-02-22 16:41:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-193), ATR 10; pole 3 x ATR[1]; flag zone 33 % of the pole height over the SMA 10[1]; exit 6 bars after the flag
    flagpole = close > close[1] and (close - open) > 3 ATR[1]  or  two / three rising closes with (close - open[1 or 2]) > 3 ATR[1]
    pole_top = valuewhen(flagpole, close, 0);  flag_bottom = pole_top - 0.33 (pole_top - sma(close, 10)[1]);  flag k = flagpole[k] and open, close within [flag_bottom, pole_top]
    bull_flag = flag3 and flag2[1] and flag1[2] -> entry Long;  barssince(bull_flag) == 6 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * pole_top is the most recent pole's close at each bar, so a new pole inside the window moves the
      zone, as written. The six-bar count runs from the latest flag; a flag while long is refused
      (default pyramiding) but restarts the count. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, flagpole and flag pattern.
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

NAME = "fmz_442543_bull_flag_six_bar_exit_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pole_mult": [3.0, 2.0],
    "exit_bars": [6, 12],
}
DEFAULT_PARAMS = {"pole_mult": 3.0, "exit_bars": 6, "atr_len": 10, "zone": 0.33}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a1 = _rma(tr, int(p["atr_len"])).shift(1) * float(p["pole_mult"])
    r1, r2, r3 = c > c.shift(1), c.shift(1) > c.shift(2), c.shift(2) > c.shift(3)
    pole = ((r1 & ((c - o) > a1)) | (r1 & r2 & ((c - o.shift(1)) > a1))
            | (r1 & r2 & r3 & ((c - o.shift(2)) > a1)))
    pv, cv = pole.to_numpy(), c.to_numpy(dtype=float)
    tv = np.full(len(cv), np.nan)
    last = np.nan
    for i in range(len(cv)):
        if pv[i]:
            last = cv[i]
        tv[i] = last
    top = pd.Series(tv, index=c.index)
    bottom = top - float(p["zone"]) * (top - c.rolling(10).mean().shift(1))
    inside = (o >= bottom) & (o <= top) & (c >= bottom) & (c <= top)
    flag = {k: pole.shift(k, fill_value=False) & inside for k in (1, 2, 3)}
    bull = (flag[3] & flag[2].shift(1, fill_value=False) & flag[1].shift(2, fill_value=False)).to_numpy()
    k = int(p["exit_bars"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, lastf = False, -1
    for i in range(m):
        if bull[i]:
            lastf = i
        if bull[i] and not held:
            le[i] = True
        elif held and lastf >= 0 and i - lastf == k:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
