"""PSAR flip with a TTM-squeeze momentum cross above the EMA 100, 1-hour bars: from flat, the close crossing over the SAR (0.02 / 0.02 / 0.2) with the squeeze oscillator crossing over zero above the EMA 100
goes long, the mirror short; a close crossing the stored 20-bar swing stop or its 1.125 R target closes; entries only from flat.
Port of FMZ strategy #442372 "Trading Psychology Balancing Strategy" (Octopus Nest Strategy).

FMZ source id: 442372

Source
    https://www.fmz.com/strategy/442372 (PineScript v5, FMZ last modified 2024-02-21 14:33:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 200-529), source close; PSAR adaptive off (ta.sar 0.02, 0.02, 0.2); EMA 100; TTM 20; swing stop look-back 20 x 0.98; RR 1.125
    enterLong = close > ema100 and crossover(close, psar) and crossover(osc, 0), osc = linreg(close - ((highest(20) + lowest(20)) / 2 + sma(close, 20)) / 2, 20, 0);  short mirrored;  isTradeOpen filters repeats
    on a kept long signal: longSL = lowest(low, 20) == low ? high 0.98 : lowest(low, 20) 0.98;  longTP = close (1 + (1 - longSL / close) 1.125)  (shorts mirrored with 1.02)
    exitLong = (crossunder(close, longSL) or crossover(close, longTP)) and long -> close, isTradeOpen = '';  enterLong and flat -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Is PSAR Adaptive?" off the SAR is ta.sar(0.02, 0.02, 0.2); the adaptive block is computed but
      unused. The isTradeOpen state and the stored levels are ported as written. The exits are bar-close
      tests of the close crossing the stored levels, sent at the next open (no broker stop). Entries need a
      flat position: opposite entries cannot occur (entries only from flat). No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR / squeeze-momentum crosses with close-tested swing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442372_psar_ttm_cross_ema100_swing_levels"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [100, 200],
    "rr": [1.125, 2.0],
}
DEFAULT_PARAMS = {"ema_length": 100, "rr": 1.125, "ttm_length": 20, "lookback": 20, "sl_mult": 0.98,
                  "sl_backup": 0.98, "psar_start": 0.02, "psar_inc": 0.02, "psar_max": 0.2}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar reference block: the SAR value (NaN on the first bar)."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
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
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def _linreg_end(x, n):
    """Pine linreg(x, n, 0): the least-squares line over the last n values, valued at the current bar."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float)
        tm = t.mean()
        ym = w.mean(axis=1)
        slope = ((w - ym[:, None]) @ (t - tm)) / ((t - tm) ** 2).sum()
        out[n - 1:] = ym + slope * (n - 1 - tm)
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    psar = pd.Series(_sar(hv, lv, cv, float(p["psar_start"]), float(p["psar_inc"]), float(p["psar_max"])), index=c.index)
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    t = int(p["ttm_length"])
    e1 = (h.rolling(t).max() + lo.rolling(t).min()) / 2 + c.rolling(t).mean()
    osc = _linreg_end(c - e1 / 2, t)
    raw_l = ((c > ema) & (c > psar) & (c.shift(1) <= psar.shift(1)) & (osc > 0) & (osc.shift(1) <= 0)).to_numpy()
    raw_s = ((c < ema) & (c < psar) & (c.shift(1) >= psar.shift(1)) & (osc < 0) & (osc.shift(1) >= 0)).to_numpy()
    lb = int(p["lookback"])
    ll = lo.rolling(lb).min().to_numpy()
    hh = h.rolling(lb).max().to_numpy()
    sm, sb, rr = float(p["sl_mult"]), float(p["sl_backup"]), float(p["rr"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    ito = ""
    lsl = ssl = 0.0
    ltp = stp = np.nan
    lsl1 = ssl1 = 0.0
    ltp1 = stp1 = np.nan
    for i in range(m):
        el, es = bool(raw_l[i]), bool(raw_s[i])
        if ito == "":
            if el:
                ito = "long"
            elif es:
                ito = "short"
        elif ito == "long" and el:
            el = False
        elif ito == "short" and es:
            es = False
        if el:
            if ll[i] == lv[i]:
                lsl = hv[i] * sb
            elif ll[i] > 0:
                lsl = ll[i] * sm
        if es:
            if hh[i] == hv[i]:
                ssl = hv[i] * (1 + (1 - sb))
            elif hh[i] > 0:
                ssl = hh[i] * (1 + (1 - sm))
        if el:
            ltp = cv[i] * (1 + (1 - lsl / cv[i]) * rr)
        if es and ssl:
            stp = cv[i] * (1 - (1 - cv[i] / ssl) * rr)
        cp = cv[i - 1] if i > 0 else np.nan
        x_l = held == 1 and ((cv[i] < lsl and cp >= lsl1) or (cv[i] > ltp and cp <= ltp1))
        x_s = held == -1 and ((cv[i] > ssl and cp <= ssl1) or (cv[i] < stp and cp >= stp1))
        new = held
        if x_l:
            new, ito = 0, ""
        if x_s:
            new, ito = 0, ""
        if el and held == 0:
            new = 1
        if es and held == 0:
            new = -1
        tgt[i] = new
        held = new
        lsl1, ssl1, ltp1, stp1 = lsl, ssl, ltp, stp
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
