"""EMA 9 / 26 crossings, 1-hour bars: the cross up goes long and the cross down goes short, each with a 90-tick stop and a 270-tick target from the signal close (0.06 / 0.18 ATR at the 1-hour reading); reversing.
Port of FMZ strategy #458051 "高级EMA交叉策略基于动态止损和获利目标的自适应交易系统Advanced-EMA-Crossover-Strategy-Adaptive-Trading-System-with-Dynamic-Stop-Loss-and-Take-Profit-Targets" (EMA Crossover Strategy with Fixed Stop Loss, Take Profit, and Alerts).

FMZ source id: 458051

Source
    https://www.fmz.com/strategy/458051 (PineScript v5, FMZ last modified 2024-07-29 15:20:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-189), EMA 9 / 26; stop 90 ticks, target 270 ticks (x mintick) from the signal close
    crossover(ema9, ema26) -> entry Long, exit(stop = close - 90 ticks, limit = close + 270 ticks);  crossunder -> entry Short, exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 90 / 270 ticks are 9 / 27 at the 0.1 tick, ported as ATR multiples at the 1-hour reading
      (~150): 0.06 / 0.18 ATR 14 from the bar before the fill. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, EMA crossings.
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

NAME = "fmz_458051_ema9_26_cross_tick_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.06, 1.0],
    "tp_atr": [0.18, 3.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.06, "tp_atr": 0.18, "atr_len": 14, "fast": 9, "slow": 26}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
