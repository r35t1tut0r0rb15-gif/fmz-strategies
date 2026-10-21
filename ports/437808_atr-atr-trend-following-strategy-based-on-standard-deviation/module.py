"""Inverted ATR trailing-line crossings, 4-hour bars: the close crossing below the ATR(11) x 0.5 trailing line goes long, crossing above it goes short; reversing (as written, against the usual direction).
Port of FMZ strategy #437808 "基于ATR和标准差通道的趋势跟踪交易策略ATR-Trend-Following-Strategy-Based-on-Standard-Deviation-Channel" (Average True Range Strategy).

FMZ source id: 437808

Source
    https://www.fmz.com/strategy/437808 (PineScript v2, FMZ last modified 2024-01-05 16:34:27).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 160-197), ATR 11, multiplier 0.5; date window true; standard-deviation bands plotted only
    xATRTrailingStop: the classic ratchet (max(prev, close - nLoss) while both closes are above it, min(prev, close + nLoss) while both are below, else reset to the close's side)
    pos = -1 when close crosses above the line, 1 when it crosses below, else pos[1];  pos == 1 -> entry Long, exit(Long, when = take);  pos == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level, so the entry is sent on every bar of the state; pos 0 (before the first
      crossing) sends nothing. The strategy.exit carries no price or distance, so it places no order.
      The crossing signs are as written (long after a close falls through the line; owed: probably the
      reverse). strategy.entry reverses: REVERSAL INTENDED. The initial_capital variable is unused; no
      sizing code. FREQ = "4h" from the backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing line.
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

NAME = "fmz_437808_atr_trail_line_inverted"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [0.5, 1.0],
    "atr_period": [11, 22],
}
DEFAULT_PARAMS = {"atr_mult": 0.5, "atr_period": 11}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nl = (float(p["atr_mult"]) * _atr(bars_df, p["atr_period"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    st = np.zeros(m)
    for i in range(m):
        pv = ts[i - 1] if i > 0 and not np.isnan(ts[i - 1]) else 0.0     # nz(xATRTrailingStop[1], 0)
        c1 = cv[i - 1] if i > 0 else np.nan
        x = cv[i]
        if not np.isnan(nl[i]):
            if x > pv and c1 > pv:
                ts[i] = max(pv, x - nl[i])
            elif x < pv and c1 < pv:
                ts[i] = min(pv, x + nl[i])
            elif x > pv:
                ts[i] = x - nl[i]
            else:
                ts[i] = x + nl[i]
        prev = st[i - 1] if i > 0 else 0.0
        if c1 < pv and x > pv:
            st[i] = -1.0
        elif c1 > pv and x < pv:
            st[i] = 1.0
        else:
            st[i] = prev
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
