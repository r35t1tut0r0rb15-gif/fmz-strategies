"""Two EMAs with stochastic RSI pivots (PtGambler), 5-minute bars: in an EMA 50 > EMA 200 trend a pull-back under the EMA
50 with K under 20 (from flat) arms a long, which a K / D cross up with a higher K pivot-low reading then triggers; the
stop is the ATR band under the signal bar's low and the target twice that distance (mirror for shorts).
Port of FMZ strategy #430898 "Oma and Apollo Dual Rail Trading Strategy" (2 EMA + Stoch RSI + ATR [Pt]).

FMZ source id: 430898

Source
    https://www.fmz.com/strategy/430898 (PineScript v5, FMZ last modified 2023-11-02 17:09:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 181-346), EMA 50 / 200, stoch RSI 3 / 3 / 14 / 14, ATR band EMA 14 x 0.7, RR 2
    trigger L := ema1 > ema2 and close < ema1 and k < 20 and flat (latched until an entry or ema1 < ema2)
    L_entry = trigger L[1] and crossover(k, d) and valuewhen(pivotlow(k, 1, 1), k, 0) > valuewhen(pivotlow(k, 1, 1), k, 1)
    flat: L_SL = low - 0.7 x ema(tr, 14), L_PT = close + (close - L_SL) x 2; one bar after the entry bar L_PT is re-based
    exit("Exit Long", limit = L_PT, stop = L_SL) every bar (mirror short with high + band, ema1 < ema2, k > 80)

Interpretation choices (Pine rules in SURVEY_README.md)
    * valuewhen(P_lo, k, n) reads k on the bars where the pivot is confirmed (one bar after the pivot
      bar), as written, not the pivot's own value. Pivots are strict (as #430840).
    * The stop and target are set on the flat signal bar; one bar after the entry bar the target is
      re-based on that bar's close and band (a moving level): rule 2, mark trailing_stop_pending. The
      port keeps the signal bar's levels, as fractions of its close, shifted one bar.
    * "Flat" (for arming) follows the house bracket on bars. An armed entry may reverse an open
      opposite position: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The date
      window is dropped. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-based target fixed at entry (rule 2).
    2 generic: PASS, EMAs, stochastic RSI and an ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430898_two_ema_stoch_rsi_atr"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [0.7, 1.5],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"ema1": 50, "ema2": 200, "smooth_k": 3, "smooth_d": 3, "rsi_len": 14, "stoch_len": 14,
                  "atr_len": 14, "atr_mult": 0.7, "rr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _pivots(x, lb, rb, high):
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def _recent(x, piv):
    """valuewhen(piv, x, 0) and valuewhen(piv, x, 1)."""
    m = len(x)
    r0, r1 = np.full(m, np.nan), np.full(m, np.nan)
    a = b = np.nan
    for t in range(m):
        if piv[t]:
            a, b = x[t], a
        r0[t], r1[t] = a, b
    return r0, r1


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean().to_numpy()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean().to_numpy()
    r = _rsi(c, int(p["rsi_len"]))
    s = int(p["stoch_len"])
    k = (100 * (r - r.rolling(s).min()) / (r.rolling(s).max() - r.rolling(s).min()).replace(0.0, np.nan)
         ).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    xup = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    xdn = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    kv = k.to_numpy(dtype=float)
    rh, ph = _recent(kv, _pivots(kv, 1, 1, True))
    rl, pl = _recent(kv, _pivots(kv, 1, 1, False))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    band = (tr.ewm(span=int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"])).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    rr = float(p["rr"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    trig_l = trig_s = False
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        bull, bear = e1[i] > e2[i], e1[i] < e2[i]
        l_entry = trig_l and xup[i] and rl[i] > pl[i]
        s_entry = trig_s and xdn[i] and rh[i] < ph[i]
        fresh_l = bull and cv[i] < e1[i] and kv[i] < 20 and pos == 0
        fresh_s = bear and cv[i] > e1[i] and kv[i] > 80 and pos == 0
        trig_l = (not (l_entry or bear or s_entry)) if trig_l else fresh_l
        trig_s = (not (s_entry or bull or l_entry)) if trig_s else fresh_s
        dist_l = (cv[i] - (lv[i] - band[i])) / cv[i]
        dist_s = ((hv[i] + band[i]) - cv[i]) / cv[i]
        if l_entry and pos != 1 and dist_l > 0:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, dist_l, dist_l * rr
            sl_arr[i], tp_arr[i] = s_, t_
        elif s_entry and pos != -1 and dist_s > 0:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, dist_s, dist_s * rr
            sl_arr[i], tp_arr[i] = s_, t_
    return le, se, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
