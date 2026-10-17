"""Close crossing above the Parabolic SAR while RSI 14 is oversold, long only, with a 3 % stop / 5 % target, 1-hour
bars: the close crossing above SAR(0.02, 0.02, 0.2) with RSI(14) below 30 goes long; the close crossing below the SAR
with RSI above 70 closes it.
Port of FMZ strategy #483528 "动态RSI与PSAR交叉策略结合风险管理系统-Dynamic-RSI-and-PSAR-Crossover-Strategy-with-Risk-Management-System" (PSAR & RSI Strategy with Risk Management).

FMZ source id: 483528

Source
    https://www.fmz.com/strategy/483528 (PineScript v5, FMZ last modified 2025-02-24 10:27:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-149), SAR 0.02 / 0.02 / 0.2, RSI 14, 30 / 70, TP 5 %, SL 3 %
    buy = crossover(close, psar) and rsi < 30 -> entry long + exit(limit = close x 1.05, stop = close x 0.97)
    sell = crossunder(close, psar) and rsi > 70 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar's close: 3 % / 5 % fractions re-based on the fill
      (house rule). A later buy signal while held re-places it from the new close: mark trailing_stop_pending; the port
      keeps the entry's bracket.
    * ta.sar as TradingView documents it (_sar_pine, as #428699).
    * Long only; the source has no shorts. The sell close is an exit signal (never on a buy bar). Stop module:
      portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, Parabolic SAR, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483528_psar_cross_rsi_oversold_long_bracket"
FAMILY = "parabolic_sar"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_os": [30, 40],
    "tp_pct": [5.0, 8.0],
}
DEFAULT_PARAMS = {"psar_start": 0.02, "psar_inc": 0.02, "psar_max": 0.2, "rsi_len": 14, "rsi_os": 30, "rsi_ob": 70,
                  "tp_pct": 5.0, "sl_pct": 3.0}


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


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


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
    sar = _sar_pine(bars_df, p["psar_start"], p["psar_inc"], p["psar_max"])
    rsi = _rsi(c, int(p["rsi_len"]))
    x_up = (c > sar) & (c.shift(1) <= sar.shift(1))
    x_dn = (c < sar) & (c.shift(1) >= sar.shift(1))
    long_e = (x_up & (rsi < p["rsi_os"])).astype(bool)
    long_x = (x_dn & (rsi > p["rsi_ob"]) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
