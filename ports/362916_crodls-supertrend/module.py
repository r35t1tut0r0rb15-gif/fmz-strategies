"""Two of three SuperTrends (3 x 12, 2 x 11, 1 x 10) agreeing, the open on the EMA 200 side, a 13-bar signed volume-times-change sum on the same side and a Stochastic 14 turn, 30-minute bars: up-trends with the stochastic crossing up under 30 go long, down-trends with it crossing down over 70 go short; reversing.
Port of FMZ strategy #362916 "Crodls Supertrend" (Crodl's Supertrend).

FMZ source id: 362916

Source
    https://www.fmz.com/strategy/362916 (PineScript v5, FMZ last modified 2022-05-13 17:43:21).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 56-134), SuperTrend 3 / 12, 2 / 11, 1 / 10; EMA 200; t = sum(volume x change, 13); Stoch 14, K 1, D 3
    long = ((d1 < 0 and d2 < 0) or (d2 < 0 and d3 < 0) and (d1 < 0 or d3 < 0)) and open > ema200 and t > 0 and k < 30 and crossover(k, d)
    short mirror (d > 0, open < ema200, t < 0, k > 70, crossover(d, k));  long -> entry Long;  else short -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or", so the trend test is (d1 and d2 up) or (d2 and d3 up), as written. t sums
      volume x (close - close[1]) over 13 bars (0 on unchanged bars). An indicator() script sending
      strategy orders on FMZ; its SMA smoothing line is display only. REVERSAL INTENDED. No sizing code.
      FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend agreement with trend, volume-flow and stochastic filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in t = sum(volume x (close - close[1]), 13); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362916_triple_supertrend_ema200_volume_flow_stoch_turn_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [200, 100],
    "flow_len": [13, 26],
}
DEFAULT_PARAMS = {"ema_len": 200, "flow_len": 13, "period_k": 14, "smooth_k": 1, "period_d": 3}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    d1 = _supertrend(bars_df, 3.0, 12)[1]
    d2 = _supertrend(bars_df, 2.0, 11)[1]
    d3 = _supertrend(bars_df, 1.0, 10)[1]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    t = (v * c.diff()).rolling(int(p["flow_len"])).sum()
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["period_d"])).mean()
    up_t = ((d1 < 0) & (d2 < 0)) | ((d2 < 0) & (d3 < 0) & ((d1 < 0) | (d3 < 0)))
    dn_t = ((d1 > 0) & (d2 > 0)) | ((d2 > 0) & (d3 > 0) & ((d1 > 0) | (d3 > 0)))
    le = up_t & (o > ema) & (t > 0) & (k < 30) & (k > d) & (k.shift(1) <= d.shift(1))
    se = dn_t & (o < ema) & (t < 0) & (k > 70) & (d > k) & (d.shift(1) <= k.shift(1)) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
