"""SuperTrend direction with the Ichimoku cloud and an EMA 200 filter, 1-hour bars: the close above the displaced cloud in a SuperTrend (ATR 10 x 3) uptrend, with the EMA 200 outside the cloud, goes long,
the mirror short; the close under the SuperTrend line or a down trend closes a long (mirrored for shorts); reversing.
Port of FMZ strategy #441963 "Multitimeframe Trend Hunter Strategy" (TrendHunter [Blocky]).

FMZ source id: 441963

Source
    https://www.fmz.com/strategy/441963 (PineScript v5, FMZ last modified 2024-02-18 10:17:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-489), HTF "60" = the chart's own 1h; EMA 200; SuperTrend hl2, ATR 10 x 3; Ichimoku 9 / 26 / 52, displacement 26; defaults: price outside cloud, SuperTrend transitions, EMA outside cloud; HTF and LTF exits; 80 % of equity
    emaSmooth = security(HTF, ema200, gaps_on)[1];  [up, dn, trend] = KivancOzbilgic SuperTrend (hl2, 10, 3);  HTF SuperTrend = security(HTF, same, lookahead_on)
    long = close > max(SSA[26], SSB[26]) and HTF_trend == 1 and (emaSmooth > max(SSA[26], SSB[26]) or emaSmooth < min(..)) -> entry Long;  short mirrored -> entry Short
    exitLong = close < HTF_up or HTF_trend == -1 or close < up or trend == -1 -> close Long;  exitShort = close > HTF_dn or HTF_trend == 1 or close > dn or trend == 1 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The higher timeframe is "60" on a 1-hour chart, the chart's own bars: the HTF SuperTrend equals the
      chart's, emaSmooth is the EMA 200 one bar back, the Ichimoku lines are the chart's, and the cloud is
      read 26 bars back (displacement 26 x 1h / 1h). With the default options only the cloud, SuperTrend and
      EMA-outside-cloud tests apply (the others return na, which counts as true). A close acts only on the
      held position; a close written after a reversing entry leaves the reversal standing (as #438020).
      REVERSAL INTENDED. The 80 % of equity size and capital are sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend, Ichimoku cloud and EMA filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
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

NAME = "fmz_441963_supertrend_ichimoku_cloud_ema_filter"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 14],
    "multiplier": [3.0, 2.0],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0, "ema_len": 200, "conv": 9, "base": 26, "span2": 52,
                  "displacement": 26}


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


def _supertrend(bars_df, n, mult):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = (mult * _rma(tr, n)).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m, dtype=np.int8)
    pu = pd_ = np.nan
    t = 1
    for i in range(m):
        uc, dc = src[i] - a[i], src[i] + a[i]
        u1 = uc if np.isnan(pu) else pu
        d1 = dc if np.isnan(pd_) else pd_
        cp = cv[i - 1] if i > 0 else np.nan
        u = max(uc, u1) if cp > u1 else uc
        d = min(dc, d1) if cp < d1 else dc
        if t == -1 and cv[i] > d1:
            t = 1
        elif t == 1 and cv[i] < u1:
            t = -1
        up[i], dn[i], trend[i] = u, d, t
        pu, pd_ = u, d
    return up, dn, trend


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema_s = c.ewm(span=int(p["ema_len"]), adjust=False).mean().shift(1)

    def don(k):
        return (lo.rolling(k).min() + h.rolling(k).max()) / 2

    ssa = (don(int(p["conv"])) + don(int(p["base"]))) / 2
    ssb = don(int(p["span2"]))
    dsp = int(p["displacement"])
    top = pd.concat([ssa.shift(dsp), ssb.shift(dsp)], axis=1).max(axis=1, skipna=False)
    bot = pd.concat([ssa.shift(dsp), ssb.shift(dsp)], axis=1).min(axis=1, skipna=False)
    up, dn, trend = _supertrend(bars_df, int(p["periods"]), float(p["multiplier"]))
    ema_out = ((ema_s > top) | (ema_s < bot)).to_numpy()
    cv = c.to_numpy(dtype=float)
    el = (c > top).to_numpy() & (trend == 1) & ema_out
    es = (c < bot).to_numpy() & (trend == -1) & ema_out
    xl = (cv < up) | (trend == -1)
    xs = (cv > dn) | (trend == 1)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
