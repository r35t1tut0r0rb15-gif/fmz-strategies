"""Four Ehlers filters agreeing, 2-hour bars: the Elegant Oscillator slope turning positive as the close crosses over the Decycler, with the close above a rising Instantaneous Trendline and a positive Spearman
rank signal, goes long; the mirror short; the close of 100 bars ago crossing the trendline closes; reversing.
Port of FMZ strategy #442966 "Quantitative Oscillation Indicator Combination Strategy" (Ehlers Combo (Elegant Oscillator + Decycler + Instantaneous Trendline + Spearman Rank)).

FMZ source id: 442966

Source
    https://www.fmz.com/strategy/442966 (PineScript v5, FMZ last modified 2024-02-27 16:46:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-264), source close; length 20; RMS length 50; resolution (chart)
    EO: deriv = close - nz(close[2]);  rms = sqrt(math.avg(deriv^2, 50));  iFish = tanh(deriv / rms);  ss = SuperSmoother(iFish, 20);  sig = sign of ss - wma(ss, 20), 2 when growing
    Decycler dec(20); ITrend(alpha 2 / 21 / 2); Spearman rank over 20 bars (bubble passes as written)
    long = crossover(sig, 0) and crossover(decSig, 0) and crossover(close, dec) and close > iT and iT rising and spearmanSig > 0;  exit long = crossunder(close[100], iT);  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * math.avg(deriv^2, 50) is the mean of the squared change and the number 50, as written; the 50 is
      in squared price units, so the port scales it to the close at the BTC reading of 42000 (50 x
      (close / 42000)^2), keeping the BTC behaviour (criterion 2). The Spearman block is ported with
      the script's own sort loops (growing passes, the extra j = 0 compare of the first pass included).
      The exits compare the close of 100 bars ago with the current trendline, as written. Each close
      acts only on a held position; closes are called before entries. strategy.entry reverses:
      REVERSAL INTENDED. The margin settings are sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, squared-price constant -> scaled to the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin settings stored.
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

NAME = "fmz_442966_ehlers_eo_decycler_itrend_spearman_combo"
FAMILY = "cycle_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "rms_length": [50, 100],
}
DEFAULT_PARAMS = {"length": 20, "rms_length": 50, "ref_price": 42000.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _spearman(src, n):
    m = len(src)
    out = np.zeros(m)
    for t in range(m):
        pa = np.zeros(n + 2)
        rk = np.zeros(n + 2)
        for i in range(1, n + 1):
            k = t - (i - 1)
            pa[i] = src[k] if k >= 0 and not np.isnan(src[k]) else 0.0
            rk[i] = i
        for i in range(1, n + 1):
            cnt = n + 1 - i
            hi = n - cnt
            js = range(1, hi + 1) if hi >= 1 else (1, 0)        # Pine counts down when to < from
            for j in js:
                if pa[j + 1] < pa[j]:
                    pa[j], pa[j + 1] = pa[j + 1], pa[j]
                    rk[j], rk[j + 1] = rk[j + 1], rk[j]
        s = sum((i - rk[i]) ** 2 for i in range(1, n + 1))
        out[t] = 2 * (0.5 - (1 - (6 * s) / (n * (n ** 2 - 1))))
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    n = int(p["length"])
    m = len(cv)
    # Elegant Oscillator
    a1 = np.exp(-1.414 * np.pi / n)
    b1 = 2 * a1 * np.cos(1.414 * np.pi / n)
    c2, c3 = b1, -a1 * a1
    c1 = 1 - c2 - c3
    c_2 = np.concatenate(([0.0, 0.0], cv[:-2])) if m > 2 else np.zeros(m)
    deriv = cv - c_2
    const = float(p["rms_length"]) * (cv / float(p["ref_price"])) ** 2
    rms = np.sqrt((deriv ** 2 + const) / 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        nd = np.where(rms != 0, deriv / rms, 0.0)
    ifish = np.where(nd != 0, np.tanh(nd), 0.0)
    ss = np.zeros(m)
    for i in range(m):
        if i < 3:
            ss[i] = 0.0
            continue
        ss[i] = c1 * (ifish[i] + ifish[i - 1]) / 2 + c2 * ss[i - 1] + c3 * ss[i - 2]
    ss_s = pd.Series(ss, index=c.index)
    slo = (ss_s - _wma(ss_s, n)).to_numpy()
    sig = np.zeros(m, dtype=np.int8)
    for i in range(m):
        prev = slo[i - 1] if i > 0 and not np.isnan(slo[i - 1]) else 0.0
        if slo[i] > 0:
            sig[i] = 2 if slo[i] > prev else 1
        elif slo[i] < 0:
            sig[i] = -2 if slo[i] < prev else -1
    # Decycler
    tw = 2 * np.pi / n
    alpha = (np.cos(tw) + np.sin(tw) - 1) / np.cos(tw)
    dec = np.zeros(m)
    for i in range(m):
        pc = cv[i - 1] if i > 0 else 0.0
        pd_ = dec[i - 1] if i > 0 else 0.0
        dec[i] = (alpha / 2) * (cv[i] + pc) + (1 - alpha) * pd_
    dsig = np.sign(cv - dec)
    # Instantaneous Trendline
    a = 2 / (n + 1) / 2
    it = np.zeros(m)
    for i in range(m):
        p1 = cv[i - 1] if i >= 1 else np.nan
        p2 = cv[i - 2] if i >= 2 else np.nan
        if i < 7:
            it[i] = (cv[i] + 2 * p1 + p2) / 4 if i >= 2 else np.nan
        else:
            it[i] = ((a - a * a / 4) * cv[i] + 0.5 * a * a * p1 - (a - 0.75 * a * a) * p2
                     + 2 * (1 - a) * it[i - 1] - (1 - a) * (1 - a) * it[i - 2])
    # Spearman rank
    sp = _spearman(cv, n)
    sp_slo = sp - np.concatenate(([0.0], sp[:-1]))
    sp_slo1 = np.concatenate(([0.0], sp_slo[:-1]))
    sp_sig = np.where((sp_slo > 0) | (sp > 0), np.where(sp_slo > sp_slo1, 2, 1),
                      np.where((sp_slo < 0) | (sp < 0), np.where(sp_slo < sp_slo1, -2, -1), 0))
    sig1 = np.concatenate(([0], sig[:-1]))
    dsig1 = np.concatenate(([0.0], dsig[:-1]))
    cd, cd1 = cv - dec, np.concatenate(([np.nan], (cv - dec)[:-1]))
    it1 = np.concatenate(([np.nan], it[:-1]))
    with np.errstate(invalid="ignore"):
        e_long = ((sig > 0) & (sig1 <= 0) & (dsig > 0) & (dsig1 <= 0) & (cd > 0) & (cd1 <= 0)
                  & (cv > it) & (it1 < it) & (sp_sig > 0))
        e_short = ((sig < 0) & (sig1 >= 0) & (dsig < 0) & (dsig1 >= 0) & (cd < 0) & (cd1 >= 0)
                   & (cv < it) & (it1 > it) & (sp_sig < 0))
        c100 = c.shift(100).to_numpy()
        c101 = c.shift(101).to_numpy()
        x_long = (c100 < it) & (c101 >= it1)
        x_short = (c100 > it) & (c101 <= it1)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if x_long[i] and held == 1:
            new = 0
        if x_short[i] and held == -1:
            new = 0
        if e_long[i] and new != 1:
            new = 1
        if e_short[i] and new != -1:
            new = -1
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
