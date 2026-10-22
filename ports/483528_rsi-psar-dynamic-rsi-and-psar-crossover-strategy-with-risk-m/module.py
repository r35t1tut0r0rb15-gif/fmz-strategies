"""Close crossings of the Parabolic SAR 0.02 / 0.02 / 0.2 with RSI 14 extremes, hourly bars, long only: crossing up with RSI under 30 goes long with a 3 % stop and a 5 % target from the signal close; crossing down with RSI over 70 closes.
Port of FMZ strategy #483528 "动态RSI与PSAR交叉策略结合风险管理系统-Dynamic-RSI-and-PSAR-Crossover-Strategy-with-Risk-Management-System" (PSAR & RSI Strategy with Risk Management).

FMZ source id: 483528

Source
    https://www.fmz.com/strategy/483528 (PineScript v5, FMZ last modified 2025-02-24 10:27:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-149), SAR 0.02 / 0.02 / 0.2; RSI 14 / 70 / 30; target 5 %; stop 3 %; 10 % of equity
    crossover(close, sar) and rsi < 30 -> entry Buy + exit(limit = close x 1.05, stop = close x 0.97);  crossunder(close, sar) and rsi > 70 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar as Pine documents it (the house _sar helper, as #458200). The levels are fixed at the signal
      close and sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256). A repeat signal while held re-sends the bracket; stops() keeps the first, so
      the repeat case is marked trailing_stop_pending (as #434428). Long only; Opposite entries cannot
      occur. Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, SAR crossings with RSI extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483528_sar_cross_rsi14_extreme_3_5pct_bracket_long"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_percent": [5.0, 3.0],
    "sl_percent": [3.0, 2.0],
}
DEFAULT_PARAMS = {"tp_percent": 5.0, "sl_percent": 3.0, "psar_start": 0.02, "psar_increment": 0.02,
                  "psar_max": 0.2, "rsi_length": 14}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["psar_start"]), float(p["psar_increment"]), float(p["psar_max"])), index=c.index)
    r = _rsi(c, int(p["rsi_length"]))
    le = (c > sar) & (c.shift(1) <= sar.shift(1)) & (r < 30)
    lx = (c < sar) & (c.shift(1) >= sar.shift(1)) & (r > 70)
    a, b = float(p["sl_percent"]) / 100, float(p["tp_percent"]) / 100
    return le, lx, {"l_sl": c * (1 - a), "l_tp": c * (1 + b)}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, (lx | (lf & l_thr)) & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
