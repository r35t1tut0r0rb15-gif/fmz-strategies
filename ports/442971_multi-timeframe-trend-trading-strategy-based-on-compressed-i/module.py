"""Boom Hunter Pro trigger crossings with a Hull 480 trend and a volatility spike, 1-hour bars: the quotient trigger crossing over the red wave, a rising Hull with the close above it and a body above one
deviation go long (unless long), the mirror short (unless short); the stop at the lower of close - ATR and the 20-bar low, the target three times that distance; reversing.
Port of FMZ strategy #442971 "Multi Timeframe Trend Trading Strategy Based on Compressed Indicators" (Boom Hunter + Hull Suite + Volatility Oscillator Strategy).

FMZ source id: 442971

Source
    https://www.fmz.com/strategy/442971 (PineScript v5, FMZ last modified 2024-02-27 17:40:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-427), EOT 1: LPPeriod 6, K1 0; EOT 2: LPPeriod 28, K2 0.3; Hull (Hma) 200 x 2.4; volLength 80; swing 20; ATR 14; R:R 3; risk 3 % sizing; dates (true)
    HP = 2-pole high-pass (100 x 0.707);  Filt = SuperSmoother(HP, LP);  Peak = max(|Filt|, 0.991 Peak[1]);  X = Filt / Peak;  q1 = (X + K1) / (K1 X + 1) x 60 + 50 (trigger = sma(q1, 1));  q4 the same with LP 28, K2 0.3
    long = crossover(trigger, q4) and hull > hull[2] and close > hull and (close - open) > stdev(close - open, 80);  not long -> entry Long, exit(stop = min(close - atr, lowest(low, 20)), limit = close + 3 x stop distance)
    short mirrored (close < hull[2], body < -stdev) -> entry Short with the mirrored bracket

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed on the signal bar: sl_stop = (close - stop) / close of the signal bar and
      tp_stop = 3 x that, shifted one bar inside stops() and re-based on the fill (shorts mirrored).
      Entries are refused only on the held side, so the opposite entry reverses: REVERSAL INTENDED. The
      Hull length is int(200 x 2.4) = 480 (HMA of 240 / 480 / 22). The risk-based quantity and the
      commission are sizing and costs. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, roofing-filter quotients with a Hull trend and a volatility spike.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity and commission stored.
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

NAME = "fmz_442971_boom_hunter_hull_vol_spike_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lp_period": [6, 10],
    "swing_length": [20, 50],
}
DEFAULT_PARAMS = {"lp_period": 6, "swing_length": 20, "k1": 0.0, "lp_period2": 28, "k2": 0.3, "hull_len": 480,
                  "vol_length": 80, "atr_len": 14, "rr": 3.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _quotient(cv, lp, k):
    m = len(cv)
    al = (np.cos(.707 * 2 * np.pi / 100) + np.sin(.707 * 2 * np.pi / 100) - 1) / np.cos(.707 * 2 * np.pi / 100)
    a1 = np.exp(-1.414 * np.pi / lp)
    b1 = 2 * a1 * np.cos(1.414 * np.pi / lp)
    c2, c3 = b1, -a1 * a1
    c1 = 1 - c2 - c3
    hp, filt, q = np.zeros(m), np.zeros(m), np.zeros(m)
    peak = 0.0
    for i in range(m):
        x1 = cv[i - 1] if i >= 1 else 0.0
        x2 = cv[i - 2] if i >= 2 else 0.0
        h1 = hp[i - 1] if i >= 1 else 0.0
        h2 = hp[i - 2] if i >= 2 else 0.0
        hp[i] = (1 - al / 2) ** 2 * (cv[i] - 2 * x1 + x2) + 2 * (1 - al) * h1 - (1 - al) ** 2 * h2
        f1 = filt[i - 1] if i >= 1 else 0.0
        f2 = filt[i - 2] if i >= 2 else 0.0
        filt[i] = c1 * (hp[i] + h1) / 2 + c2 * f1 + c3 * f2
        peak = 0.991 * peak
        if abs(filt[i]) > peak:
            peak = abs(filt[i])
        x = filt[i] / peak if peak != 0 else 0.0
        q[i] = (x + k) / (k * x + 1)
    return q * 60 + 50


def _bracket(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    n = int(p["swing_length"])
    lsl = np.minimum(c - atr, lo.rolling(n).min())
    ssl = np.maximum(c + atr, h.rolling(n).max())
    lf = (1 - lsl / c).abs()
    sf = (1 - ssl / c).abs()
    return lf, sf


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    cv = c.to_numpy(dtype=float)
    trig = pd.Series(_quotient(cv, int(p["lp_period"]), float(p["k1"])), index=c.index)
    q4 = pd.Series(_quotient(cv, int(p["lp_period2"]), float(p["k2"])), index=c.index)
    boom_l = (trig > q4) & (trig.shift(1) <= q4.shift(1))
    boom_s = (trig < q4) & (trig.shift(1) >= q4.shift(1))
    hl = int(p["hull_len"])
    hull = _wma(2 * _wma(c, hl // 2) - _wma(c, hl), int(np.floor(np.sqrt(hl) + 0.5)))
    shull = hull.shift(2)
    spike = c - o
    sd = spike.rolling(int(p["vol_length"])).std(ddof=0)
    lg = boom_l & (hull > shull) & (c > hull) & (spike > sd)
    sh = boom_s & (hull < shull) & (c < shull) & (spike < -sd)
    return lg.to_numpy(), sh.to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh = _signals(bars_df, p)
    lf_s, sf_s = _bracket(bars_df, p)
    lf, sf = lf_s.to_numpy(), sf_s.to_numpy()
    rr = float(p["rr"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + rr * s_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - rr * s_)):
                pos = 0
        if i + 1 >= m:
            continue
        if lg[i] and pos != 1 and not np.isnan(lf[i]):
            le[i], pos, entry_i, s_ = True, 1, i + 1, lf[i]
        elif sh[i] and pos != -1 and not np.isnan(sf[i]):
            se[i], pos, entry_i, s_ = True, -1, i + 1, sf[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh = _signals(bars_df, p)
    lf, sf = _bracket(bars_df, p)
    ix = bars_df.index
    frac = pd.Series(np.where(sh, sf.to_numpy(), lf.to_numpy()), index=ix)
    return {"sl_stop": frac.shift(1), "tp_stop": (float(p["rr"]) * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
