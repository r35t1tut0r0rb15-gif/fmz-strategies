"""Dow-theory trend changes from confirmed pivots with a tick bracket, 2-minute bars: when the last two pivot highs and
the last two pivot lows (10 / 10) both rise the trend turns up and the strategy goes long; when both fall it turns down
and goes short; each trade has a stop and a target twice as far (ticks in the source, ATR multiples here).
Port of FMZ strategy #489309 "道氏理论趋势自适应动量策略Dow-Theory-Trend-Adaptive-Momentum-Strategy" (Dow Theory Trend Strategy v3).

FMZ source id: 489309

Source
    https://www.fmz.com/strategy/489309 (PineScript v5, FMZ last modified 2025-04-03 13:05:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 121-217), pivots 10 / 10, SL 100 ticks, TP 200 ticks, mode Auto
    a new pivot high (low) different from the last one shifts last -> prev
    up = last high > prev high and last low > prev low -> trend 1;  down = both lower -> trend -1;  else keep
    trend changes to 1 -> entry long + exit(loss = 100, profit = 200 ticks);  to -1 -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow(10, 10): strictly above (below) the 10 bars on each side, known 10 bars later; a pivot
      equal to the last one is not stored, as written.
    * Criterion 2: the tick distances become sl_atr / 2 x sl_atr x Wilder ATR(14) of the signal bar: 100 ticks of
      0.01 on the author's 2-minute BNB_USDT (about 600) are 0.17 %, about 1.5 two-minute ATR (judgement before any
      backtest). loss / profit are measured from the fill, as the house stops.
    * Entries reverse (REVERSAL INTENDED); the trend cannot change both ways on one bar.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed after their right bars.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489309_dow_pivot_trend_change_bracket"
FAMILY = "pivot_reversal"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pivot": [10, 5],
    "sl_atr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"pivot": 10, "sl_atr": 1.5, "tp_ratio": 2.0, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _pivot_at(x, t, n, high):
    j = t - n
    if j - n < 0:
        return np.nan
    v = x[j]
    left, right = x[j - n:j], x[j + 1:t + 1]
    if np.isnan(v) or np.isnan(left).any() or np.isnan(right).any():
        return np.nan
    ok = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return v if ok else np.nan


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    n = int(p["pivot"])
    m = len(hv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_h = prev_h = last_l = prev_l = np.nan
    trend = prev_trend = 0
    for t in range(m):
        ph, pl = _pivot_at(hv, t, n, True), _pivot_at(lv, t, n, False)
        if not np.isnan(ph) and (np.isnan(last_h) or ph != last_h):
            prev_h, last_h = last_h, ph
        if not np.isnan(pl) and (np.isnan(last_l) or pl != last_l):
            prev_l, last_l = last_l, pl
        if not (np.isnan(last_h) or np.isnan(prev_h) or np.isnan(last_l) or np.isnan(prev_l)):
            if last_h > prev_h and last_l > prev_l:
                trend = 1
            elif last_h < prev_h and last_l < prev_l:
                trend = -1
        if trend != prev_trend:
            le[t], se[t] = trend == 1, trend == -1
        prev_trend = trend
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": d.shift(1), "tp_stop": (p["tp_ratio"] * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
