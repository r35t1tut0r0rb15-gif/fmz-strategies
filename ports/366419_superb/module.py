"""A volume-price shadow line (EMA 10 of the high / low pushed by a volume-weighted spread's deviation from its SMA 14) with an ATR 10 band and a 5 % reversal trend tracker, 4-hour bars: the tracker turning up goes long, turning down goes short; reversing.
Port of FMZ strategy #366419 "SuperB" (SuperB).

FMZ source id: 366419

Source
    https://www.fmz.com/strategy/366419 (PineScript v4, FMZ last modified 2022-05-29 10:40:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 34-170), shadow windows 28 / 14; EMA 10; ATR 10 x 1; reversal factor 0.05
    spreadvol = (close - open) x 100 x volume / ((high - low) x 100);  vp = spreadvol + cum(spreadvol);  shadow = (vp - sma(vp, 14)) / stdev(vp - sma(vp, 14), 28) x stdev(high - low, 28)
    out = shadow > 0 ? high + shadow : low + shadow;  vpt = ema(out, 10);  up / dn = vpt -/+ atr(10);  trend flips when dn < hb[1] (1 - 0.05) / up > lb[1] (1 + 0.05)
    buy = crossover(time of the last up flip, time of the last down flip) -> entry buy;  else sell -> entry sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cumulative sum only enters through vp minus its own SMA (and that difference's deviation), so its
      starting point cancels, as written. A bar with no range has an undefined spread-volume, read as 0 in
      the running sum. The trend tracker is kept as written (seeded on the first two bars; hb / lb carried
      with nz, compared with their raw previous values). The buy / sell crossings of the flip times are
      the flips themselves. A study() script sending strategy orders on FMZ; the header is a spot pair and
      the shorts are ported as written (as #428970). REVERSAL INTENDED. No sizing code. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-price shadow line with a percent reversal tracker.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG366419 (2 members, best partner #435238, Jaccard 0.846); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the spread-volume (close - open) x volume / range of the shadow line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366419_volume_spread_shadow_ema10_atr_band_pct_reversal_tracker"
FAMILY = "atr_trailing_line"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [10, 20],
    "factor": [0.05, 0.02],
}
DEFAULT_PARAMS = {"len": 10, "factor": 0.05, "st_mult": 1.0, "st_period": 10, "window_len": 28, "v_len": 14}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    rng = (h - lo) * 100
    spreadvol = ((c - o) * 100 * v / rng.where(rng != 0)).fillna(0.0)
    vp = spreadvol + spreadvol.cumsum()
    w, vl = int(p["window_len"]), int(p["v_len"])
    price_spread = (h - lo).rolling(w).std(ddof=0)
    dev = vp - vp.rolling(vl).mean()
    shadow = dev / dev.rolling(w).std(ddof=0) * price_spread
    out = (h + shadow).where(shadow > 0, lo + shadow)
    vpt = out.ewm(span=int(p["len"]), adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["st_period"])) * float(p["st_mult"])
    up_a, dn_a = (vpt - atr).to_numpy(dtype=float), (vpt + atr).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    fac = float(p["factor"])
    m = len(cv)
    trend = np.zeros(m)
    hb_p = lb_p = hl_p = l1_p = np.nan
    t_p = 0.0
    for i in range(m):
        hb = 0.0 if np.isnan(hb_p) else hb_p
        lb = 0.0 if np.isnan(lb_p) else lb_p
        hl = 0.0 if np.isnan(hl_p) else hl_p
        l1 = 0.0 if np.isnan(l1_p) else l1_p
        t = t_p
        x, n = up_a[i], dn_a[i]
        if i == 0:
            lb, hb, l1, hl = n, x, cv[i], cv[i]
        elif i == 1:
            if x >= hb_p:
                hb, hl, t = x, cv[i], 1.0
            else:
                lb, l1, t = n, cv[i], -1.0
        else:
            if t_p > 0:
                hl = max(hl_p, cv[i]) if not np.isnan(hl_p) else cv[i]
                if x >= hb_p:
                    hb = x
                elif n < hb_p - hb_p * fac:
                    lb, l1, t = n, cv[i], -1.0
            else:
                l1 = min(l1_p, cv[i]) if not np.isnan(l1_p) else cv[i]
                if n <= lb_p:
                    lb = n
                elif x > lb_p + lb_p * fac:
                    hb, hl, t = x, cv[i], 1.0
        trend[i] = t
        hb_p, lb_p, hl_p, l1_p, t_p = hb, lb, hl, l1, t
    tr_s = pd.Series(trend, index=c.index)
    le = (tr_s == 1) & (tr_s.shift(1) == -1)
    se = (tr_s == -1) & (tr_s.shift(1) == 1)
    return le, pd.Series(False, index=c.index), se, pd.Series(False, index=c.index)


def portfolio_kwargs(**params):
    return {}
