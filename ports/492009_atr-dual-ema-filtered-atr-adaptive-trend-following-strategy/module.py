"""UT Bot on Heikin-Ashi closes with an EMA 10 / 50 filter and a tick trail, hourly bars: the Heikin-Ashi close
crossing above the ATR trailing line with the fast EMA above the slow one goes long, the mirror goes short; each
trade trails a stop a few ticks behind the best price.
Port of FMZ strategy #492009 "双均线过滤的ATR自适应趋势跟踪策略-Dual-EMA-Filtered-ATR-Adaptive-Trend-Following-Strategy" (UTBot + EMA Filter (HA + ATR Logic)).

FMZ source id: 492009

Source
    https://www.fmz.com/strategy/492009 (PineScript v5, FMZ last modified 2025-04-25 15:01:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 153-206), ATR 20 x 1.0, EMA 10 / 50 of the source, Heikin-Ashi on
    sr = Heikin-Ashi close (same timeframe);  trail = the UT Bot ratchet of sr -+ 1.0 x ATR(20)
    buy = sr[1] < trail[1] and sr > trail and emaFast > emaSlow;  sell = the mirror with emaFast < emaSlow
    entry long on buy, short on sell (strategy.entry reverses); strategy.close on the opposite signal
    exit(trail_points = 10, trail_offset = 10, limit = sr +- 100) every bar while in a position

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(heikinashi, timeframe.period, close) on the chart's own timeframe is the current bar's
      Heikin-Ashi close (o + h + l + c) / 4, complete at the bar's close. The ATR is the chart bars' Wilder ATR.
    * The trailing line is the source's: nz(trail[1]) is 0 before the first value, as written.
    * strategy.close on the opposite signal falls on the bar whose entry reverses anyway (a close written after an
      entry does not undo the reversal).
    * The limit sr +- 100 is in PRICE units: on the author's DOGE_USDT (about 0.2) the long target is unreachable and
      the short target is below zero, so it is inert; dropped (criterion 2) and quoted in original_sizing.txt.
    * The trail is ported natively (mark trailing_stop): {"type": "volatility", "atr_n": 20, "k": 0.05,
      "anchor": "high_low", "activate_after": 0.0005}. Stated approximation: Pine trails 10 ticks behind the best
      price after 10 ticks of profit; 10 ticks of 0.00001 on DOGE at about 0.2 are 0.05 % of price, about
      0.05 x the hourly ATR(20) (judgement before any backtest).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> ATR multiple; the inert price-unit target dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_492009_utbot_heikin_ashi_ema_filter"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.0, 2.0],
    "trail_k": [0.05, 0.5],
}
DEFAULT_PARAMS = {"atr_len": 20, "atr_mult": 1.0, "ema_fast": 10, "ema_slow": 50, "use_heikin": True,
                  "trail_k": 0.05, "trail_activate": 0.0005}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _ut_trail(sr, nloss):
    m = len(sr)
    out = np.full(m, np.nan)
    prev = 0.0                              # nz(trail[1])
    for i in range(m):
        s, nl = sr[i], nloss[i]
        if np.isnan(s) or np.isnan(nl):     # na in Pine; nz() reads it as 0 on the next bar
            prev = 0.0
            continue
        s1 = sr[i - 1] if i > 0 else np.nan
        iff_1 = s - nl if s > prev else s + nl
        if s < prev and (not np.isnan(s1)) and s1 < prev:
            iff_2 = min(prev, s + nl)
        else:
            iff_2 = iff_1
        if s > prev and (not np.isnan(s1)) and s1 > prev:
            t = max(prev, s - nl)
        else:
            t = iff_2
        out[i] = t
        prev = t
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[x] for x in ("open", "high", "low", "close"))
    sr = (o + h + lo + c) / 4 if p["use_heikin"] else c
    nloss = p["atr_mult"] * _atr(bars_df, int(p["atr_len"]))
    trail = pd.Series(_ut_trail(sr.to_numpy(dtype=float), nloss.to_numpy(dtype=float)), index=bars_df.index)
    ef = sr.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = sr.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    buy = ((sr.shift(1) < trail.shift(1)) & (sr > trail) & (ef > es)).astype(bool)
    sell = ((sr.shift(1) > trail.shift(1)) & (sr < trail) & (ef < es)).astype(bool)
    # buy and sell cannot fall on one bar (sr above and below the line); every signal bar is an entry, as Pine
    # (after a trailing exit the next signal re-enters; a same-side signal while held is ignored by both)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
