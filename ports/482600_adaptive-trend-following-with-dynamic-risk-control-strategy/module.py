"""Closes crossing the Parabolic SAR (0.02 / 0.02 / 0.2) on the EMA 50 side with an RSI 14 filter, hourly bars, entries only from flat: a cross up over the EMA with RSI over 40 goes long, a cross down under it with RSI under 60 goes short; the stop 1.3 ATR and the 0.7 % target are re-sent every bar from the latest close (pending), and the loop closes the trade on the bar a re-sent level is touched.
Port of FMZ strategy #482600 "Adaptive Trend Following with Dynamic Risk Control Strategy" (妮可百分百).

FMZ source id: 482600

Source
    https://www.fmz.com/strategy/482600 (PineScript v6, FMZ last modified 2025-02-19 11:26:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-156), SAR 0.02 / 0.02 / 0.2; ATR 14 x 1.3; TP 0.7 %; EMA 50; RSI 14, 40 / 60
    crossover(close, sar) and close > ema50 and rsi > 40 and flat -> entry B;  crossunder(close, sar) and close < ema50 and rsi < 60 and flat -> entry S
    every bar: exit B (stop = close - 1.3 atr, limit = close x 1.007);  exit S (stop = close + 1.3 atr, limit = close x 0.993)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so during each held bar the levels come
      from the bar before: stops() cannot express a level re-set every bar, so it is kept pending (as
      #438034, mark trailing_stop_pending). Because entries come only from flat, the loop follows those
      re-sent levels on each bar's high / low (as #449508) and sends the close at that bar's close (one bar
      late, not at the level); a new entry on that bar of the same side keeps the position, of the other
      side reverses it. Opposite entries cannot occur otherwise (entries only from flat). No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; re-sent bracket followed in the loop (pending).
    2 generic: PASS, SAR crossings with EMA and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482600_sar_cross_ema50_rsi_resent_atr_pct_bracket_flat_only"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multiplier": [1.3, 2.0],
    "take_profit_percent": [0.007, 0.015],
}
DEFAULT_PARAMS = {"atr_multiplier": 1.3, "take_profit_percent": 0.007, "start": 0.02, "increment": 0.02,
                  "maximum": 0.2, "atr_length": 14, "ema_length": 50, "rsi_length": 14}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["start"]), float(p["increment"]), float(p["maximum"])), index=c.index)
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    lc = ((c > sar) & (c.shift(1) <= sar.shift(1)) & (c > ema) & (r > 40)).to_numpy()
    sc = ((c < sar) & (c.shift(1) >= sar.shift(1)) & (c < ema) & (r < 60)).to_numpy()
    d = (_atr(bars_df, int(p["atr_length"])) * float(p["atr_multiplier"])).to_numpy(dtype=float)
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tpp = float(p["take_profit_percent"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        if pend in (1, -1):
            pos = pend                            # the entry fills at this open
        elif pend == 2:
            pos = 0
        pend = 0
        held, hit = pos, False
        if i > 0 and pos == 1:
            hit = lv[i] <= cv[i - 1] - d[i - 1] or hv[i] >= cv[i - 1] * (1 + tpp)
        elif i > 0 and pos == -1:
            hit = hv[i] >= cv[i - 1] + d[i - 1] or lv[i] <= cv[i - 1] * (1 - tpp)
        flat = pos == 0 or hit                    # a level re-sent at the bar before is touched
        new = 0
        if flat and lc[i]:
            new = 1
        elif flat and sc[i]:
            new = -1
        if hit and new == held:
            continue                              # same side again: the position is kept
        if hit and new == 0:
            (lx if held == 1 else sx)[i] = True   # closed at this bar's close (one bar late)
            pend = 2
        elif new == 1:
            le[i], pend = True, 1
        elif new == -1:
            se[i], pend = True, -1
    idx = c.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
