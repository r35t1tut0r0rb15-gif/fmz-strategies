"""SMA 74 / 70 crosses from flat, with a stop 353 USD and a target 1059 USD from the entry on the author's BTC_USDT
(read as 0.35 / 1.05 ATR), four-hour bars.
Port of FMZ strategy #482437 "基于移动平均线的自适应趋势跟踪策略-Adaptive-Trend-Following-Strategy-Based-on-Moving-Average-Crossover" (Bitcoin Strategy by Jag).

FMZ source id: 482437

Source
    https://www.fmz.com/strategy/482437 (PineScript v5, FMZ last modified 2025-02-18 14:23:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 90-125), "short" SMA 74, "long" SMA 70, offset 353 USD, target 3 x offset
    flat and crossover(sma74, sma70) -> entry long; flat and crossunder -> entry short
    while held: exit(stop = avg price -/+ 353, limit = avg price +/- 1059)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 353 / 1059 USD distances are price units (criterion 2): ATR multiples judged on the author's BTC_USDT
      4-hour bars of 2024-25 (ATR about 1000): 0.35 ATR stop, 1.05 ATR target, from the signal bar's ATR (as
      #489333). They are measured from strategy.position_avg_price: applied from the fill (decision owed as
      #489289). The input name says trailing, but the levels do not move.
    * Flat-only entries with stops: simulate() mirrors the house bracket from the fill bar (as #430254); an entry is
      allowed on the bar a stop is hit. The date window is switched off in the source (withinDateRange = true).
    * Stop module: portfolio_kwargs {} (D4). FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket from the fill.
    2 generic: PASS, SMAs and ATR multiples (the USD distances converted).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: trade size 1; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries from flat only).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482437_sma74_70_cross_flat_atr_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.35, 1.0],
    "fast": [74, 20],
}
DEFAULT_PARAMS = {"fast": 74, "slow": 70, "atr_len": 14, "sl_atr": 0.35, "tp_mult": 3.0}


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


def _fracs(bars_df, p):
    return (p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy()


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    buy = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    sl, k = _fracs(bars_df, p), p["tp_mult"]
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + k * s_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - k * s_)):
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
    sl = pd.Series(_fracs(bars_df, p), index=bars_df.index).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_mult"] * sl}


def portfolio_kwargs(**params):
    return {}
