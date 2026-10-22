"""Ichimoku cloud, SuperTrend and EMA 200 confluence, 1-hour bars: a close above the displaced cloud in a SuperTrend (10 x 3) uptrend with the previous bar's EMA 200 outside the cloud goes long, the mirror
goes short; a close under the SuperTrend's up line or a downtrend closes a long, the mirror closes a short; reversing (the other filters are off by default).
Port of FMZ strategy #444971 "TrendHunter-w-MF-多时间框架趋势策略TrendHunter-w-MF-Multi-Timeframe-Trend-Strategy" (TrendHunter w/MF [Blocky]).

FMZ source id: 444971

Source
    https://www.fmz.com/strategy/444971 (PineScript v5, FMZ last modified 2024-03-15 16:01:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 193-660), EMA 200 (previous bar); SuperTrend ATR 10 x 3 on hl2; Ichimoku 9 / 26 / 52, displacement 26; WaveTrend 9 / 12 and Money Flow 60 x 190 (filters off); 80 % of equity, capital 1000
    filters on by default: price outside cloud (close vs max / min of SSA[26], SSB[26]), SuperTrend direction, EMA outside cloud;  off (na): price vs EMA, EMA above / below cloud, money flow, WaveTrend, WT overbought
    long = close > max(SSA[26], SSB[26]) and trend == 1 and (emaSmooth > max or emaSmooth < min) -> entry Long;  short mirrored -> entry Short
    close < up or trend == -1 -> close Long;  close > dn or trend == 1 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default switches, f_checkCondition is true only when the three active filters are all
      true (an off filter returns na and passes). The requests on the chart's own period ("") return
      the chart's values; emaSmooth is the previous bar's EMA 200 (the [1] on historical bars). The
      cloud is SSA / SSB 26 bars back (displacement 26 on the chart period); ta.lowest / ta.highest
      without a source use low / high. The SuperTrend follows the script's nz() seeds with Wilder's ATR.
      Calls run in order: a close acts only on a position held into the bar and not reversed by that
      bar's entry. REVERSAL INTENDED. The 80 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the cloud and EMA from completed bars.
    2 generic: PASS, cloud, SuperTrend and EMA confluence with SuperTrend exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 80 % of equity size and capital stored.
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

NAME = "fmz_444971_cloud_supertrend_ema200_confluence_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [3.0, 2.0],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"multiplier": 3.0, "ema_len": 200, "periods": 10, "conv": 9, "base": 26, "span_b": 52, "displacement": 26}


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


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _classic_supertrend(h, lo, c, mult, n):
    """calcSuperTrend as written: up / dn lines with nz() seeds, trend starts at 1."""
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ups, dns, trs = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    up_p = dn_p = np.nan
    d = 1
    for i in range(m):
        u, dd = src[i] - mult * atr[i], src[i] + mult * atr[i]
        u1 = u if np.isnan(up_p) else up_p
        d1 = dd if np.isnan(dn_p) else dn_p
        if i > 0 and cv[i - 1] > u1:
            u = _nmax(u, u1) if not np.isnan(u) else u
        if i > 0 and cv[i - 1] < d1:
            dd = _nmin(dd, d1) if not np.isnan(dd) else dd
        if d == -1 and cv[i] > d1:
            d = 1
        elif d == 1 and cv[i] < u1:
            d = -1
        ups[i], dns[i], trs[i] = u, dd, d
        up_p, dn_p = u, dd
    return ups, dns, trs


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn, tr = _classic_supertrend(h, lo, c, float(p["multiplier"]), int(p["periods"]))

    def mid(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    ssa = (mid(p["conv"]) + mid(p["base"])) / 2
    ssb = mid(p["span_b"])
    k = int(p["displacement"])
    a26, b26 = ssa.shift(k), ssb.shift(k)
    cmax = np.maximum(a26, b26).to_numpy()   # nan if either is nan
    cmin = np.minimum(a26, b26).to_numpy()
    es = c.ewm(span=int(p["ema_len"]), adjust=False).mean().shift(1).to_numpy()
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        outside = (es > cmax) | (es < cmin)
        lc = (cv > cmax) & (tr == 1) & outside
        sc = (cv < cmin) & (tr == -1) & outside
        xl = (cv < up) | (tr == -1)
        xs = (cv > dn) | (tr == 1)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and pos != 1:
            le[i], new = True, 1
        elif sc[i] and pos != -1:
            se[i], new = True, -1
        if xl[i] and pos == 1 and new == 1:      # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if xs[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
