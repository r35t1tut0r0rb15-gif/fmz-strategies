"""SuperTrend (ATR 10 x 3) flips filtered by an ATR volatility regime (its place in the 100-bar ATR range), 10-minute bars: a flip up in the low-volatility regime with the close above the line goes long, a flip down in the high-volatility regime below it goes short, each with a 2 ATR stop and 3 ATR target from the signal close; reversing.
Port of FMZ strategy #478712 "Machine Learning Adaptive SuperTrend Quantitative Trading Strategy" (Adaptive SuperTrend Strategy).

FMZ source id: 478712

Source
    https://www.fmz.com/strategy/478712 (PineScript v5, FMZ last modified 2025-01-17 15:11:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-160), ATR 10; factor 3; training length 100; regimes at 75 / 50 / 25 % of the ATR range; SL 2 ATR, TP 1.5 x SL; 200 % of equity
    cluster = atr >= lower + 0.75 (upper - lower) ? 0 : atr >= mid ? 1 : 2;  [st, dir] = supertrend(3, atr10)
    crossunder(dir, 0) and cluster > 1 and close > st -> entry Long + exit(limit = close + 3 atr, stop = close - 2 atr);  crossover(dir, 0) and cluster == 0 and close < st -> entry Short + exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's SuperTrend is Pine's reference one (direction -1 = up-trend), so crossunder(dir, 0) is
      a flip up. The bracket is sent on each signal bar from its close and ATR: the opening signal's
      levels are ported, sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256); a later flip up inside a long (after a flip down that did not
      short) re-sends it, which is not followed (as #434428, mark trailing_stop_pending). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 200 % of equity size is sizing. FREQ =
      "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, SuperTrend flips in ATR regimes with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_478712_supertrend_flip_atr_regime_atr_bracket_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "training": [100, 300],
}
DEFAULT_PARAMS = {"factor": 3.0, "training": 100, "atr_len": 10, "atr_mult": 2.0}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    vol = _rma(tr, int(p["atr_len"]))
    n = int(p["training"])
    up_v, lo_v = vol.rolling(n).max(), vol.rolling(n).min()
    hi_reg = vol >= lo_v + (up_v - lo_v) * 0.75
    mid_reg = vol >= lo_v + (up_v - lo_v) * 0.5
    low_reg = ~hi_reg & ~mid_reg              # cluster 2, also while the range is na (comparisons false)
    line, d = _supertrend(bars_df, float(p["factor"]), int(p["atr_len"]))
    flip_up = (d < 0) & (d.shift(1) >= 0)
    flip_dn = (d > 0) & (d.shift(1) <= 0)
    le = flip_up & low_reg & (c > line)
    se = flip_dn & hi_reg & (c < line)
    sl = float(p["atr_mult"]) * vol
    lvl = {"l_sl": c - sl, "l_tp": c + 1.5 * sl, "s_sl": c + sl, "s_tp": c - 1.5 * sl}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
