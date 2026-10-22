"""MACD crossings and a close / weighted-average side, both gated by the RSI 14 being higher than 60 bars ago, 2-hour bars: with the RSI over 50, a MACD cross up over its SMA 14 or a close over the squared-weight WMA 20 goes long; with the RSI under 50 the mirrors go short; an RSI over 70 (under 30) with the same gate closes; reversing.
Port of FMZ strategy #453287 "MACD和RSI结合的自然交易策略-MACD-and-RSI-Combined-Natural-Trading-Strategy" (Improved MACD and RSI Trading Strategy).

FMZ source id: 453287

Source
    https://www.fmz.com/strategy/453287 (PineScript v5, FMZ last modified 2024-06-03 17:22:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-187), MACD 12 / 26 / 9 with its SMA 14; RSI 14; gate change(RSI, 60) > 0; WMA 20 with weights (20 - i)^2; 100 % of equity, commission 0.01 %
    crossover(macd, signal) and macd > sma14(macd) and rsi < 70, gate and rsi > 50 -> entry Long;  the mirror and rsi < 50 -> entry Short
    gate and rsi > 70 -> close Long;  gate and rsi < 30 -> close Short
    close > wma20, gate and rsi > 50 -> entry Long WMA;  close < wma20, gate and rsi < 50 -> entry Short WMA;  the same closes for the WMA ids

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'tf_1h' gate is the RSI against its value 60 bars back (not a timeframe). The calls run in
      source order with the trade ids followed: an entry on the held side is ignored whatever its id,
      an opposite entry reverses, and a close acts only on its own id held into the bar when no earlier
      call reversed it. So an RSI-over-70 bar closes a 'Long' trade and the 'Long WMA' state entry can
      re-open it at once (a round trip that keeps the position, now under 'Long WMA'), while a 'Long
      WMA' trade is closed. REVERSAL INTENDED. The 100 % of equity and the commission are stored.
      FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD / WMA entries behind an RSI momentum gate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing and commission stored.
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

NAME = "fmz_453287_macd_wma_rsi_gate_id_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "gate_len": [60, 30],
    "wma_len": [20, 50],
}
DEFAULT_PARAMS = {"rsi_len": 14, "gate_len": 60, "wma_len": 20, "ma_len": 14}


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


def _sq_wma(x, n):
    """The source's wma(): weights (n - i)^2 on x[i], i = 0 .. n - 1."""
    n = int(n)
    tot = sum((n - k) ** 2 for k in range(n))
    return sum(x.shift(k) * (n - k) ** 2 for k in range(n)) / tot


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    mma = macd.rolling(int(p["ma_len"])).mean()
    gate = (r - r.shift(int(p["gate_len"]))) > 0
    up_x = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn_x = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    wma = _sq_wma(c, p["wma_len"])
    l1 = (up_x & (macd > mma) & (r < 70) & gate & (r > 50)).to_numpy()
    s1 = (dn_x & (macd < mma) & (r > 30) & gate & (r < 50)).to_numpy()
    l2 = ((c > wma) & gate & (r > 50)).to_numpy()
    s2 = ((c < wma) & gate & (r < 50)).to_numpy()
    xl = (gate & (r > 70)).to_numpy()
    xs = (gate & (r < 30)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pid = 0, ""
    for i in range(m):
        cur, cid = pos, pid

        def enter(d, name):
            nonlocal cur, cid
            if cur != d:
                cur, cid = d, name

        def close(d, name):
            nonlocal cur, cid
            if pos == d and pid == name and cur == d and cid == name:
                cur, cid = 0, ""

        if l1[i]:
            enter(1, "Long")
        if s1[i]:
            enter(-1, "Short")
        if xl[i]:
            close(1, "Long")
        if xs[i]:
            close(-1, "Short")
        if l2[i]:
            enter(1, "Long WMA")
        if s2[i]:
            enter(-1, "Short WMA")
        if xl[i]:
            close(1, "Long WMA")
        if xs[i]:
            close(-1, "Short WMA")
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos, pid = cur, cid
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
