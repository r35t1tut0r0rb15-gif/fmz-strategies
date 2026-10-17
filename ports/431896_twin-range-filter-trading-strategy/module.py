"""Twin range filter (colinmck, greenmask9), 30-minute bars: the close turning above the twin-range filter (fast 27 x 1.6,
slow 55 x 2) after a short state, with the 32-bar SMA of the true range under its 64-bar RMA, goes long (mirror short);
a 900-tick target and 300-tick stop as ATR fractions, and a time exit 17 bars after the signal.
Port of FMZ strategy #431896 "Twin Range Filter Trading Strategy" (Twin Range Filter Algo).

FMZ source id: 431896

Source
    https://www.fmz.com/strategy/431896 (PineScript v4, FMZ last modified 2023-11-13 10:38:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 171-285), range 27 x 1.6 / 55 x 2, ATR 32 SMA < 64 RMA, profit 900 / stop 300 ticks, time stop 17
    smrng = (ema(ema(|close - close[1]|, t), 2t - 1) x m for both pairs) / 2;  filt = range filter of close by smrng
    longCond = close > filt and upward > 0 (rising or falling close);  long = longCond and CondIni[1] == -1 (mirror short)
    bull = long and sma(tr, 32) < rma(tr, 64) -> entry long, exit(profit 900, loss 300 ticks)
    barssince(bull) == 17 -> close long (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the target and stop are 900 / 300 ticks (90 / 30 USD on BTC_USDT at mintick 0.1,
      about 0.75 / 0.25 ATR on 30-minute BTC); they become tp_atr / sl_atr x the Wilder ATR 14 of the
      signal bar, as fractions of its close, fixed at entry.
    * The time exit is a close-checked exit 17 bars after the signal bar (not a time stop); it acts
      only on a position of that side and does not undo a reversal. "Flat" follows the house bracket
      on bars. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; close-checked time exit.
    2 generic: ADAPT, tick target / stop -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the floor(capital / close) order size stored in original_sizing.txt.
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

NAME = "fmz_431896_twin_range_filter"
FAMILY = "range_filter_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.75, 3.0],
    "max_bars": [17, 40],
}
DEFAULT_PARAMS = {"per1": 27, "mult1": 1.6, "per2": 55, "mult2": 2.0, "l2": 32, "l3": 64, "atr_len": 14,
                  "tp_atr": 0.75, "max_bars": 17}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def smooth(t, mlt):
        avr = (c - c.shift(1)).abs().ewm(span=t, adjust=False).mean()
        return avr.ewm(span=2 * t - 1, adjust=False).mean() * mlt
    rng = ((smooth(int(p["per1"]), p["mult1"]) + smooth(int(p["per2"]), p["mult2"])) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    filt = np.zeros(m)
    prev = 0.0
    for i in range(m):
        x, r = cv[i], rng[i]
        if np.isnan(r):
            f = x
        elif x > prev:
            f = prev if x - r < prev else x - r
        else:
            f = prev if x + r > prev else x + r
        filt[i] = f
        prev = f
    upw = np.zeros(m)
    dnw = np.zeros(m)
    for i in range(1, m):
        upw[i] = upw[i - 1] + 1 if filt[i] > filt[i - 1] else (0 if filt[i] < filt[i - 1] else upw[i - 1])
        dnw[i] = dnw[i - 1] + 1 if filt[i] < filt[i - 1] else (0 if filt[i] > filt[i - 1] else dnw[i - 1])
    c1 = np.concatenate(([np.nan], cv[:-1]))
    lc = (cv > filt) & ((cv > c1) | (cv < c1)) & (upw > 0)
    sc = (cv < filt) & ((cv < c1) | (cv > c1)) & (dnw > 0)
    ini = np.zeros(m)
    q = 0
    for i in range(m):
        q = 1 if lc[i] else (-1 if sc[i] else q)
        ini[i] = q
    ini1 = np.concatenate(([0], ini[:-1]))
    cs = c.shift(1)
    tr = pd.concat([h - lo, (h - cs).abs(), (lo - cs).abs()], axis=1).max(axis=1).where(cs.notna(), h - lo)
    a2 = tr.rolling(int(p["l2"])).mean().to_numpy()
    a3 = _rma(tr, int(p["l3"]))
    calm = a2 < a3
    bull = lc & (ini1 == -1) & calm
    bear = sc & (ini1 == 1) & calm
    af = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c).to_numpy()
    tp_a = float(p["tp_atr"])
    sl_a = tp_a / 3
    mb = int(p["max_bars"])
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, e_i, s_, t_ = 0, -1, np.nan, np.nan
    last_bull = last_bear = -10 ** 9
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            e = ov[e_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        start = pos
        if bull[i]:
            last_bull = i
            if pos != 1:
                le[i], pos, e_i, s_, t_ = True, 1, i + 1, af[i] * sl_a, af[i] * tp_a
                sl_arr[i], tp_arr[i] = s_, t_
        if bear[i]:
            last_bear = i
            if pos != -1:
                se[i], pos, e_i, s_, t_ = True, -1, i + 1, af[i] * sl_a, af[i] * tp_a
                sl_arr[i], tp_arr[i] = s_, t_
        if start == 1 and pos == 1 and i - last_bull == mb:
            lx[i], pos = True, 0
        if start == -1 and pos == -1 and i - last_bear == mb:
            sx[i], pos = True, 0
    le &= ~se
    return le, lx, se, sx, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_arr, tp_arr = _run(bars_df, p)[4:]
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
