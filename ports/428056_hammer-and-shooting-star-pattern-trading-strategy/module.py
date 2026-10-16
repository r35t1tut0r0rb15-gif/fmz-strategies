"""Hammers and stars, 2-hour bars: from flat, a hammer (body in the top third of a bar no bigger than
3 ATR) goes long and a shooting star (body in the bottom third) goes short; the stop sits one ATR
beyond the two-bar extreme and the target at 1 R.
Port of FMZ strategy #428056 "Hammer and Shooting Star Pattern Trading Strategy" (Hammers & Stars v1.0).

FMZ source id: 428056

Source
    https://www.fmz.com/strategy/428056 (PineScript v4, FMZ last modified 2023-09-28 11:11:35).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 198-331), ATR 14, filter <= 3 ATR, stop 1 ATR, R:R 1, fib 0.333
    hammer = min(open, close) >= high - range x 0.333 and range <= 3 atr and close != open
    star = max(open, close) <= low + range x 0.333 and range <= 3 atr and close != open
    long (flat): stop = min(low, low[1]) - atr, target = close + (close - stop) x 1; short mirrors
    exit(limit = target, stop = stop) for the side held

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are distances from the signal close; they become fractions of that close (shifted
      one bar inside stops(), re-based on the fill), as the house convention.
    * "Flat" follows the house bracket: the loop marks the position closed once a bar's high / low
      reaches the stop or target (from the fill price).
    * The AutoView alerts, the BTC conversion security and the risk-based position size are sizing /
      messaging; the date filter is open. barstate.isconfirmed is true on history.
    * Stop module: portfolio_kwargs {} (driver D4). Opposite entries cannot occur (entries from flat).
    * Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, candle ratios and ATR multiples.
    3 crypto-exchange-only: no (the BTC_USDT security only feeds the off position sizing).
    4 signals only: risk sizing and alert settings stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428056_hammers_and_stars"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_mult": [1.0, 2.0],
    "rr": [1.0, 2.0],
    "fib": [0.333, 0.5],
}
DEFAULT_PARAMS = {"atr_len": 14, "atr_max": 3.0, "stop_mult": 1.0, "rr": 1.0, "fib": 0.333}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    rng = h - lo
    ok = (rng <= p["atr_max"] * atr) & (c != o) & atr.notna()
    hammer = (np.minimum(o, c) >= h - rng * p["fib"]) & ok
    star = (np.maximum(o, c) <= lo + rng * p["fib"]) & ok
    stop_d = atr * p["stop_mult"]
    l_stop = np.minimum(lo, lo.shift(1)) - stop_d
    s_stop = np.maximum(h, h.shift(1)) + stop_d
    l_sl = (c - l_stop) / c                       # long stop distance as a fraction of the signal close
    s_sl = (s_stop - c) / c
    return hammer, star, l_sl, s_sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hammer, star, l_sl, s_sl = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    hm, st, lf, sf = hammer.to_numpy(), star.to_numpy(), l_sl.to_numpy(), s_sl.to_numpy()
    rr = float(p["rr"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, sl_f = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - sl_f) or hv[i] >= e * (1 + sl_f * rr)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + sl_f) or lv[i] <= e * (1 - sl_f * rr)):
                pos = 0
        if pos == 0 and i + 1 < m:
            if hm[i]:
                le[i] = True
                pos, entry_i, sl_f = 1, i + 1, lf[i]
            elif st[i]:
                se[i] = True
                pos, entry_i, sl_f = -1, i + 1, sf[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hammer, star, l_sl, s_sl = _setup(bars_df, p)
    sl = l_sl.where(hammer, s_sl)
    return {"sl_stop": sl.shift(1), "tp_stop": (sl * float(p["rr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
