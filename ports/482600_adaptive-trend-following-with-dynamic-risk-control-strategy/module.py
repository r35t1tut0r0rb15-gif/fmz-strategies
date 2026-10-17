"""Closes crossing the parabolic SAR on the EMA 50 side with an RSI filter, from flat only, with a 1.3 ATR stop and a
0.7 % target, hourly bars.
Port of FMZ strategy #482600 "自适应趋势跟踪与动态风控策略-Adaptive-Trend-Following-with-Dynamic-Risk-Control-Strategy" (妮可百分百).

FMZ source id: 482600

Source
    https://www.fmz.com/strategy/482600 (PineScript v6, FMZ last modified 2025-02-19 11:26:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-149), SAR 0.02 / 0.02 / 0.2, ATR 14 x 1.3, target 0.7 %, EMA 50, RSI 14
    crossover(close, sar) and close > ema50 and rsi > 40 and flat -> entry long
    crossunder(close, sar) and close < ema50 and rsi < 60 and flat -> entry short
    every bar: exit(stop = close -/+ 1.3 ATR, limit = close x (1 +/- 0.7 %)) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar from the current close and ATR (a moving level): fixed at the entry from the
      signal close (1.3 ATR / close and 0.7 %, shifted one bar inside stops(), re-based on the fill); mark
      trailing_stop_pending.
    * Flat-only entries with stops: simulate() mirrors the house bracket from the fill bar (as #430254); an entry is
      allowed on the bar a stop is hit. Opposite entries cannot occur while held.
    * ta.sar as #428699. Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, the SAR, an EMA, RSI, an ATR multiple and a percentage target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries from flat only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482600_sar_cross_ema50_rsi_flat_atr_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.3, 2.0],
    "tp_pct": [0.7, 1.5],
}
DEFAULT_PARAMS = {"af_start": 0.02, "af_inc": 0.02, "af_max": 0.2, "atr_len": 14, "atr_mult": 1.3,
                  "tp_pct": 0.7, "ema_len": 50, "rsi_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


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


def _fracs(bars_df, p):
    return (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy(), p["tp_pct"] / 100


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    sar = _sar_pine(bars_df, p["af_start"], p["af_inc"], p["af_max"])
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    buy = ((c > sar) & (c.shift(1) <= sar.shift(1)) & (c > ema) & (rsi > 40)).to_numpy()
    sell = ((c < sar) & (c.shift(1) >= sar.shift(1)) & (c < ema) & (rsi < 60)).to_numpy()
    sl, tp = _fracs(bars_df, p)
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - tp)):
                pos = 0
        if pos == 0 and i + 1 < m and not np.isnan(sl[i]):
            if buy[i]:
                le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
            elif sell[i]:
                se[i], pos, entry_i, s_ = True, -1, i + 1, sl[i]
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fracs(bars_df, p)
    return {"sl_stop": pd.Series(sl, index=bars_df.index).shift(1), "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
