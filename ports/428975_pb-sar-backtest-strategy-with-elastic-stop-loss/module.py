"""Peterbolic SAR (Casey Bowman), 2-hour bars: an extreme / setup / trigger state machine on completed bars;
a trigger that flips the trend down goes short, one that flips it up goes long.
Port of FMZ strategy #428975 "PB SAR Backtest Strategy with Elastic Stop Loss" (PB SAR BackTest - Colorbar).

FMZ source id: 428975

Source
    https://www.fmz.com/strategy/428975 (PineScript v4, FMZ last modified 2023-10-11 15:22:26).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 246-411), no strategy inputs (date range only)
    uptrend: a new high above EP -> extreme candle (EP = high, SP = low); else a close below SP -> setup candle (TP = low)
             while a trigger is armed: low < TP -> trigger candle, trend flips down (EP = low, SP = high)
             an extreme candle with no trigger disarms TP; downtrend: the mirror
    buytrigger = trigger candle and up -> entry long; selltrigger = trigger candle and not up -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On history barstate.isnew and barstate.isconfirmed are true on every bar, and the script runs at
      bar close (no intrabar settings), so the machine is evaluated once per completed bar from its own
      high / low / close: a bar-close rule, filled at the next open.
    * The waiting flags are taken at the start of each bar, as written (a setup made on a bar can be
      triggered from the next bar on).
    * strategy.exit("SHORT", "SHORT_SL") / ("LONG", "LONG_SL") name entries that do not exist: inert.
      The date range is dropped (inDateRange is true).
    * The source has no strategy parameters; criterion 5's declared starting variants: `trigger_buffer_atr`
      0 (as written) and 0.25 (the trigger needs the low / high to pass TP by 0.25 x ATR(14)).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, completed-bar state machine, bar-close orders.
    2 generic: PASS, price levels from the bars themselves only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428975_peterbolic_sar"
FAMILY = "parabolic_sar"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trigger_buffer_atr": [0.0, 0.25],
}
DEFAULT_PARAMS = {"trigger_buffer_atr": 0.0, "atr_length": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hs, ls, cs = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = cs.shift(1)
    tr = pd.concat([hs - ls, (hs - pc).abs(), (ls - pc).abs()], axis=1).max(axis=1, skipna=False)
    buf = (float(p["trigger_buffer_atr"]) * _rma(tr, int(p["atr_length"]))).fillna(0.0).to_numpy() \
        if float(p["trigger_buffer_atr"]) > 0 else np.zeros(len(c))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    if m == 0:
        idx = bars_df.index
        return tuple(pd.Series(False, index=idx) for _ in range(4))
    up = True
    ep, sp, tp = h[0], lo[0], np.nan
    for i in range(1, m):
        ext = trig = False
        wait_setup = not np.isnan(sp)
        wait_trig = not np.isnan(tp)
        if up:
            if h[i] > ep:
                ext, ep, sp = True, h[i], lo[i]
            elif wait_setup and c[i] < sp:
                sp, tp = np.nan, lo[i]
            if wait_trig:
                if lo[i] < tp - buf[i]:
                    trig, ext = True, True
                    ep, sp, tp, up = lo[i], h[i], np.nan, False
                elif ext:
                    tp = np.nan
        else:
            if lo[i] < ep:
                ext, ep, sp = True, lo[i], h[i]
            elif wait_setup and c[i] > sp:
                sp, tp = np.nan, h[i]
            if wait_trig:
                if h[i] > tp + buf[i]:
                    trig, ext = True, True
                    ep, sp, tp, up = h[i], lo[i], np.nan, True
                elif ext:
                    tp = np.nan
        if trig and up:
            le[i] = True
        elif trig and not up:
            se[i] = True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
