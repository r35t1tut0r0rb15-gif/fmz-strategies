"""Adaptive ATR trend with a loss cut at the entry open, 4-hour bars: a trend line whose ATR(2) factor follows the Bollinger width flips long or short (reversing); a bar trading back through the entry bar's open
closes the position, and a later bar clear of that price re-enters in the trend's direction.
Port of FMZ strategy #438799 "Adaptive Trend Following Strategy" ([TH] Adaptive Trend).

FMZ source id: 438799

Source
    https://www.fmz.com/strategy/438799 (PineScript v2, FMZ last modified 2024-01-15 14:20:32).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 159-223), period 2, bandwidth 50, factor 0.5-3; BB EMA 20 x 2
    factor = clip((upper - lower) / basis x 50, 0.5, 3);  TrendUp / TrendDown = hl2 -/+ factor x atr(2), ratcheted;  Trend = 1 if close > TrendDown[1], -1 if close < TrendUp[1], else Trend[1]
    price_cut = open after a signal;  loss cut = (trend 1 and low < price_cut) or (trend -1 and high > price_cut) on a bar without a trend flip;  re-entry when flat and the bar clears price_cut
    trend flip or re-entry -> entry long / short;  loss cut -> close the trend's side

Interpretation choices (Pine rules in SURVEY_README.md)
    * All tests are on closed bars and fill at the next open (the stop orders are commented out in the
      source). The script's own flags are followed: price_cut is the open of the bar after any signal
      (the fill), current_trend changes the bar after a flip, has_position starts na (no re-entry until
      the first signal). stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. FREQ = "4h" from the backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested loss cut.
    2 generic: PASS, adaptive ATR trend line and entry-price tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_438799_adaptive_trend_loss_cut"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pd_": [2, 5],
    "bw": [50, 25],
}
DEFAULT_PARAMS = {"pd_": 2, "bw": 50.0, "min_factor": 0.5, "max_factor": 3.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    basis = c.ewm(span=20, adjust=False).mean()
    dev = 2 * c.rolling(20).std(ddof=0)
    raw = (2 * dev / basis) * float(p["bw"])
    fac = raw.clip(lower=float(p["min_factor"]), upper=float(p["max_factor"]))
    fac = fac.where(raw.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["pd_"]))
    hl2 = (h + lo) / 2
    up_ = (hl2 - fac * atr).to_numpy()
    dn_ = (hl2 + fac * atr).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    tu, td = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m)
    for i in range(m):
        c1 = cv[i - 1] if i > 0 else np.nan
        tu1 = tu[i - 1] if i > 0 else np.nan
        td1 = td[i - 1] if i > 0 else np.nan
        tu[i] = max(up_[i], tu1) if (c1 > tu1 and not np.isnan(up_[i])) else up_[i]
        td[i] = min(dn_[i], td1) if (c1 < td1 and not np.isnan(dn_[i])) else dn_[i]
        prev = trend[i - 1] if i > 0 else 1.0
        trend[i] = 1.0 if cv[i] > td1 else (-1.0 if cv[i] < tu1 else prev)
    tprev = np.concatenate(([np.nan], trend[:-1]))
    stl = (tprev == -1) & (trend == 1)
    sts = (tprev == 1) & (trend == -1)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    price_cut, cur, has_pos = np.nan, 0, None
    prev_any, prev_stl, prev_sts = False, False, False
    for i in range(m):
        if prev_any:
            price_cut = ov[i]
        if prev_stl:
            cur = 1
        elif prev_sts:
            cur = -1
        if stl[i] or sts[i]:
            cut = False
        elif cur == 1:
            cut = price_cut > lv[i]
        elif cur == -1:
            cut = price_cut < hv[i]
        else:
            cut = False
        has_pos = False if cut else (True if prev_any else has_pos)
        rl = has_pos is False and cur == 1 and lv[i] > price_cut
        rs = has_pos is False and cur == -1 and hv[i] < price_cut
        if (stl[i] or rl) and i + 1 < m:
            le[i] = True
        elif (sts[i] or rs) and i + 1 < m:
            se[i] = True
        elif cut and cur == 1:
            lx[i] = True
        elif cut and cur == -1:
            sx[i] = True
        prev_any = bool(stl[i] or sts[i] or rl or rs)
        prev_stl, prev_sts = bool(stl[i]), bool(sts[i])
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
