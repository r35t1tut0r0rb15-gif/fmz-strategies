"""EMA 13 / 26 crossings, 2-hour bars: the cross up goes long and the cross down goes short; the close crossing under the EMA 13 while the RSI 7 crosses under 30 also goes long (over / over 70 short), and a cross with the close beyond both EMAs, the EMA 5 / 10 trend and an RSI extreme adds named entries; reversing.
Port of FMZ strategy #451399 "EMA交叉策略与RSI背离30分钟趋势识别和价格竭尽-EMA-Cross-Strategy-with-RSI-Divergence-30-Minute-Trend-Identification-and-Price-Exhaustion" (EMA Cross Strategy with RSI Divergence, 30-Minute Trend Identification, and Price Exhaustion).

FMZ source id: 451399

Source
    https://www.fmz.com/strategy/451399 (PineScript v5, FMZ last modified 2024-05-14 16:23:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-153), EMA 13 / 26; RSI 7, levels 30 / 70; EMA 5 / 10 trend
    crossover(ema13, ema26) -> entry Long;  crossunder -> entry Short
    cross up and crossover(close, ema26) -> close Long;  cross down and crossunder(close, ema26) -> close Short
    crossunder(close, ema13) and crossunder(rsi, 30) -> entry Bullish Divergence (long);  crossover / crossover(rsi, 70) -> entry Bearish Divergence (short)
    cross up, close > ema13 and ema26, close > ema5 and ema10, rsi < 30 -> entry Buy;  mirror -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in source order on each bar: an entry on the side already held is ignored
      (pyramiding 1, whatever the id), an opposite entry reverses, and a close acts only on the 'Long'
      ('Short') trade held into the bar when no earlier call on the bar reversed it; a close followed
      by a same-side entry on the same bar leaves the position on (a round trip at one open). The close
      only fires on a cross-up bar, where a held long came from another id or from 'Long' itself.
      REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with RSI divergence entries.
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

NAME = "fmz_451399_ema13_26_cross_rsi_divergence_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 9],
    "slow": [26, 50],
    "rsi_len": [7, 14],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 26, "rsi_len": 7, "os": 30.0, "ob": 70.0,
                  "trend_fast": 5, "trend_slow": 10}


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e13 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    e26 = c.ewm(span=int(p["slow"]), adjust=False).mean()
    e5 = c.ewm(span=int(p["trend_fast"]), adjust=False).mean()
    e10 = c.ewm(span=int(p["trend_slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    os_, ob = float(p["os"]), float(p["ob"])
    up_x, dn_x = _xover(e13, e26), _xover(e26, e13)
    close_l = (up_x & _xover(c, e26)).to_numpy()
    close_s = (dn_x & _xover(e26, c)).to_numpy()
    bull = (_xover(e13, c) & _xover(pd.Series(os_, index=c.index), r)).to_numpy()
    bear = (_xover(c, e13) & _xover(r, pd.Series(ob, index=c.index))).to_numpy()
    buy = (up_x & (c > e13) & (c > e26) & (c > e5) & (c > e10) & (r < os_)).to_numpy()
    sell = (dn_x & (c < e13) & (c < e26) & (c < e5) & (c < e10) & (r > ob)).to_numpy()
    up_x, dn_x = up_x.to_numpy(), dn_x.to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pid = 0, ""
    for i in range(m):
        cur, cid = pos, pid
        calls = []
        if up_x[i]:
            calls.append((1, "Long"))
        elif dn_x[i]:
            calls.append((-1, "Short"))
        for d, name in calls:
            if cur != d:
                cur, cid = d, name
        if close_l[i] and pos == 1 and pid == "Long" and cur == 1:
            cur = 0                          # acts only on the 'Long' trade held into the bar
        elif close_s[i] and pos == -1 and pid == "Short" and cur == -1:
            cur = 0
        later = []
        if bull[i]:
            later.append((1, "Bullish Divergence"))
        if bear[i]:
            later.append((-1, "Bearish Divergence"))
        if buy[i]:
            later.append((1, "Buy"))
        if sell[i]:
            later.append((-1, "Sell"))
        for d, name in later:
            if cur != d:
                cur, cid = d, name
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos, pid = cur, (cid if cur != 0 else "")
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
