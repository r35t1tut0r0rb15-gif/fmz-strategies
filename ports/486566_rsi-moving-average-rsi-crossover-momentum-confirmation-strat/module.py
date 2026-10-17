"""SMA 20 / 30 crosses with RSI limits and a close-checked 2 % target, long only, 1-hour bars: SMA 20 crossing above SMA
30 with RSI 14 above 25 goes long; a close 2 % above the latest buy signal's close takes profit; SMA 20 crossing below
SMA 30 with RSI below 75 closes the trade.
Port of FMZ strategy #486566 "滑动平均-RSI-交叉动量确认策略-Moving-Average-RSI-Crossover-Momentum-Confirmation-Strategy" (SMA+RSI Strategy).

FMZ source id: 486566

Source
    https://www.fmz.com/strategy/486566 (PineScript v6, FMZ last modified 2025-03-14 09:35:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 171-228), SMA 20 / 30, RSI 14 (25 / 75), TP 2 %, half TP off
    buy = crossover(sma20, sma30) and rsi > 25 -> inBuyState, entryPrice = close, entry long
    sell = crossunder(sma20, sma30) and rsi < 75 -> inSellState (inBuyState off), close long
    inBuyState and close >= entryPrice x 1.02 -> close long (full; the 50 % partial only when switched on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * inBuyState stays on after a take-profit close, and entryPrice moves with every buy signal, as written; the
      target is close-checked (an exit signal at the next open, rule 3).
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
    * The half-position option (a partial exit) is off by default: not ported. Long only: opposite entries cannot
      occur. FREQ = "1h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a close-checked target.
    2 generic: PASS, moving averages, an oscillator and a percentage.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_486566_sma20_30_cross_rsi_tp"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_pct": [2.0, 4.0],
    "sma_long": [30, 50],
}
DEFAULT_PARAMS = {"sma_short": 20, "sma_long": 30, "rsi_len": 14, "rsi_ob": 75, "rsi_os": 25, "tp_pct": 2.0,
                  "enable_tp": True}


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
    s, l = c.rolling(int(p["sma_short"])).mean(), c.rolling(int(p["sma_long"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    buy = ((s > l) & (s.shift(1) <= l.shift(1)) & (rsi > p["rsi_os"])).to_numpy()
    sell = ((s < l) & (s.shift(1) >= l.shift(1)) & (rsi < p["rsi_ob"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp = 1 + p["tp_pct"] / 100
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_buy, entry, pos = False, np.nan, 0
    for i in range(m):
        if buy[i]:
            in_buy, entry = True, cv[i]
        if sell[i]:
            in_buy = False
        start = pos
        if buy[i]:
            pos = 1
        if in_buy and p["enable_tp"] and cv[i] >= entry * tp and start == 1 and pos == 1:
            pos = 0
        if sell[i] and start == 1 and pos == 1:
            pos = 0
        le[i] = start == 0 and pos == 1
        lx[i] = start == 1 and pos == 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
