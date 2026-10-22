"""RSI 14 threshold crossings, 3-hour bars: from flat, the RSI crossing back over 30 goes long and crossing back under 70 goes short; a long closes on that sell signal (reversing to short when it is one) or an RSI at 60 or more, a short closes to flat on the buy signal or an RSI at 40 or less.
Port of FMZ strategy #473233 "RSI动态平仓位动量交易策略-RSI-Dynamic-Exit-Level-Momentum-Trading-Strategy" (RSI Strategy with Close Levels).

FMZ source id: 473233

Source
    https://www.fmz.com/strategy/473233 (PineScript v5, FMZ last modified 2024-11-28 14:59:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-148), RSI 14; entries at 30 / 70 crossings; close levels 60 / 40; inPosition flag from strategy.opentrades
    inPosition = opentrades > 0;  crossover(rsi, 30) and not inPosition -> entry Buy;  long and (crossunder(rsi, 70) or rsi >= 60) -> close Buy
    crossunder(rsi, 70) and not inPosition -> entry Sell;  short and (crossover(rsi, 30) or rsi <= 40) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flag follows the open trades at the bar's close and the order calls in the written order: the
      long entry is tested before the closes, so a short closed by a buy signal goes flat, while a long
      closed by a sell signal clears the flag before the short entry is tested and is reversed on that
      bar, as written. Otherwise entries happen only from flat. REVERSAL INTENDED (long to short only on
      a closing bar). No sizing code. FREQ = "3h" from the backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI threshold crossings with RSI close levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473233_rsi30_70_cross_rsi60_40_closes_call_order"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "close_long": [60, 70],
    "close_short": [40, 30],
}
DEFAULT_PARAMS = {"rsi_len": 14, "close_long": 60, "close_short": 40}


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
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    buy = ((r > 30) & (r.shift(1) <= 30)).to_numpy()
    sell = ((r < 70) & (r.shift(1) >= 70)).to_numpy()
    rv = r.to_numpy()
    cl, cs = float(p["close_long"]), float(p["close_short"])
    m = len(rv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        in_pos = pos != 0
        nxt = pos
        if buy[i] and not in_pos:
            le[i], in_pos, nxt = True, True, 1
        if in_pos and pos == 1 and (sell[i] or rv[i] >= cl):
            lx[i], in_pos, nxt = True, False, 0
        if sell[i] and not in_pos:
            se[i], in_pos, nxt = True, True, -1
        if in_pos and pos == -1 and (buy[i] or rv[i] <= cs):
            sx[i], in_pos, nxt = True, False, 0
        if lx[i] and se[i]:
            lx[i] = False                        # close then short on one bar: a reversal
        pos = nxt
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
