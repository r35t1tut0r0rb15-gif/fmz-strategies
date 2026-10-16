"""HPotter combo, hourly bars: the 2/20 EMA position and the Bear Power level must agree; both long holds a long,
both short holds a short, any disagreement closes everything.
Port of FMZ strategy #429466 "Short term Bearish Strategy Based on EMA Crossover and Bear Power Indicators" (Combo 2/20 EMA & Bear Power).

FMZ source id: 429466

Source
    https://www.fmz.com/strategy/429466 (PineScript v5, FMZ last modified 2023-10-17 14:00:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 176-229), EMA 14, Bear Power sell 10 / buy 1 (price units)
    EMA20: nXS = (min(low, low[1]) > ema or max(high, high[1]) < ema) ? min(low, low[1]) : max(high, high[1])
           pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    BP: value = Gimelfarb's bear-power range (candle-direction cases); value > 10 -> -1; value <= 1 -> 1; else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the Bear Power levels 10 and 1 are price units; they become sell_atr / buy_atr x Wilder
      ATR(14) of the same bar (about 0.07 / 0.007 ATR on hourly BTC, judgement before any backtest).
    * The value's nested cases are transcribed in the source's order.
    * "Trade reverse" defaults to false; the start date (2005) is dropped. A one-bar change from long to
      short reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429466 (3 members, best partner #438067, Jaccard 0.732); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429466_combo_ema_bear_power"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "sell_atr": [0.07, 0.5],
}
DEFAULT_PARAMS = {"length": 14, "sell_atr": 0.07, "buy_atr": 0.007, "atr_length": 14}


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


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    hh = pd.concat([h, h.shift(1)], axis=1).max(axis=1, skipna=False)
    ll = pd.concat([lo, lo.shift(1)], axis=1).min(axis=1, skipna=False)
    xs = ll.where((ll > xa) | (hh < xa), hh)
    c1 = c.shift(1)
    pos1 = _hold((xs < c1).to_numpy() & ~(xs > c1).to_numpy(), (xs > c1).to_numpy())
    mx = lambda a, b: np.maximum(a, b)  # noqa: E731
    conds = [c < o, c > o, (h - c) > (c - lo), (h - c) < (c - lo), c > o]
    vals = [np.where(c1 > o, mx(c - o, h - lo), h - lo),
            np.where(c1 > o, mx(c1 - lo, h - c), mx(o - lo, h - c)),
            np.where(c1 > o, mx(c1 - o, h - lo), h - lo),
            np.where(c > o, mx(c - lo, h - c), o - lo),
            mx(c1 - o, h - c)]
    default = np.where(c1 < o, mx(o - lo, h - c), h - lo)
    value = np.select([np.asarray(x, dtype=bool) for x in conds], vals, default=default)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["atr_length"])).to_numpy()
    sell = value > p["sell_atr"] * atr
    buy = value <= p["buy_atr"] * atr
    pos2 = _hold(buy & ~sell, sell)
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
