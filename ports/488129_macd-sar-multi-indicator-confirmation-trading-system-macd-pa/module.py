"""MACD phase, Parabolic SAR side and SuperTrend direction all agreeing, 2-minute bars: MACD above its signal, the close
above the SAR and an up-trending SuperTrend (10, 3) go long; all three bearish go short; a long closes when MACD and
the SAR both turn bearish (shorts mirrored).
Port of FMZ strategy #488129 "多指标协同确认交易策略MACD抛物线SAR与超级趋势三重验证系统-Multi-Indicator-Confirmation-Trading-System-MACD-Parabolic-SAR-and-Supertrend-Triple-Verification-Framework" (Vinay Strategy).

FMZ source id: 488129

Source
    https://www.fmz.com/strategy/488129 (PineScript v6, FMZ last modified 2025-03-25 11:51:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 216-268), SuperTrend 10 / 3, MACD 12 / 26 / 9, SAR 0.02 / 0.02 / 0.2
    long = macd > signal and close > sar and stDir < 0 -> entry long;  short mirrored (stDir > 0)
    macd < signal and close < sar -> close long;  macd > signal and close > sar -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction is -1 in an up-trend (Pine); ta.sar as #428699.
    * Every condition bar is an entry. Closes act on the position held at the bar's start and never undo an entry on
      that bar (#430850); a short signal while long reverses. REVERSAL INTENDED.
    * FREQ = "2min" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD, SAR and SuperTrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_488129_macd_sar_supertrend_triple"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_factor": [3.0, 2.0],
    "sar_max": [0.2, 0.1],
}
DEFAULT_PARAMS = {"st_len": 10, "st_factor": 3.0, "fast": 12, "slow": 26, "signal": 9, "sar_step": 0.02,
                  "sar_max": 0.2}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _pine_st_direction(bars_df, factor, n):
    """ta.supertrend direction: 1 = down-trend, -1 = up-trend; 0 before the ATR exists."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    d_out = np.zeros(m, dtype=np.int8)
    pu = pl = 0.0
    prev_st = np.nan
    for i in range(m):
        if np.isnan(atr[i]):
            pu = pl = 0.0
            continue
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        if i > 0:
            lw = lw if (lw > pl or c[i - 1] < pl) else pl
            up = up if (up < pu or c[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        prev_st = lw if d == -1 else up
        pu, pl = up, lw
        d_out[i] = d
    return d_out


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar), as #428699."""
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = (c.ewm(span=int(p["fast"]), adjust=False).mean()
            - c.ewm(span=int(p["slow"]), adjust=False).mean())
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    sar = _sar_pine(bars_df, p["sar_step"], p["sar_step"], p["sar_max"])
    d = _pine_st_direction(bars_df, float(p["st_factor"]), int(p["st_len"]))
    bull_m, bear_m = (macd > sig).to_numpy(), (macd < sig).to_numpy()
    above, below = (c > sar).to_numpy(), (c < sar).to_numpy()
    go_l, go_s = bull_m & above & (d < 0), bear_m & below & (d > 0)
    out_l, out_s = bear_m & below, bull_m & above
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
