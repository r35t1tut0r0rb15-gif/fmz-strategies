"""ATR Renko reversals, 1-hour bars: the Renko close (bricks of one ATR(10) built from 0, as written) moving above the Renko open goes long, below it short; a 3 % stop and 20 % target from the signal's Renko
open; reversing.
Port of FMZ strategy #440713 "基于Renko平均真实波幅的趋势反转策略Renko-ATR-Trend-Reversal-Strategy" ([tradinghook] - Renko TRS).

FMZ source id: 440713

Source
    https://www.fmz.com/strategy/440713 (PineScript v5, FMZ last modified 2024-02-01 14:30:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 181-243), ATR 10; stop 3 %, target 20 % of the Renko open; shorts on; dates 2023-07 to 2025-12 (isWithinTimeRange is true)
    renkoClose := close > p1[1] + atr ? p1[1] + atr : close < p1[1] - atr ? p1[1] - atr : p1[1] (from 0);  renkoOpen = the previous open-brick level when the open brick changes
    crossunder(renkoOpen, renkoClose) -> entry Long, strategy.exit(stop = renkoOpen x 0.97, limit = renkoOpen x 1.2);  crossover(renkoOpen, renkoClose) -> entry Short (mirrored levels)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bricks start from 0 (nz) and climb one ATR a bar until they reach the price, as written. The
      levels come from the signal bar's Renko open: sl_stop / tp_stop are their distances from the
      signal close, shifted one bar inside stops() and re-based on the fill; a level already through the
      close exits at the fill bar (sent at its close). The time-range flag is fixed true.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The
      capital, quantity and commission are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ATR Renko levels from past prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital, quantity and commission settings.
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

NAME = "fmz_440713_atr_renko_reversal_bracket"
FAMILY = "renko_bricks"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_len": [10, 20],
    "sl_pct": [3.0, 1.5],
}
DEFAULT_PARAMS = {"atr_len": 10, "sl_pct": 3.0, "tp_pct": 20.0}


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


def _brick(src, atr):
    out = np.zeros(len(src))
    prev = 0.0
    for i in range(len(src)):
        a = atr[i]
        if src[i] > prev + a:
            prev = prev + a
        elif src[i] < prev - a:
            prev = prev - a
        out[i] = prev
    return out


def _setup(bars_df, p):
    h, lo, c, o = (bars_df[k] for k in ("high", "low", "close", "open"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    rc = _brick(c.to_numpy(dtype=float), atr)
    r3 = _brick(o.to_numpy(dtype=float), atr)
    ro = np.zeros(len(rc))
    for i in range(len(rc)):
        if i > 0 and r3[i] != r3[i - 1]:
            ro[i] = r3[i - 1]
        else:
            ro[i] = ro[i - 1] if i > 0 else 0.0
    ro_s, rc_s = pd.Series(ro, index=c.index), pd.Series(rc, index=c.index)
    lsig = (ro_s < rc_s) & (ro_s.shift(1) >= rc_s.shift(1))
    ssig = (ro_s > rc_s) & (ro_s.shift(1) <= rc_s.shift(1))
    s, t = float(p["sl_pct"]) / 100, float(p["tp_pct"]) / 100
    sl = ((c - ro_s * (1 - s)) / c).where(lsig, ((ro_s * (1 + s) - c) / c).where(ssig))
    tp = ((ro_s * (1 + t) - c) / c).where(lsig, ((c - ro_s * (1 - t)) / c).where(ssig))
    ok = (sl > 0) & (tp > 0)
    return lsig.to_numpy(), ssig.to_numpy(), ok.to_numpy(), sl.where(ok), tp.where(ok)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, ok, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_, t_, imm = 0, -1, np.nan, np.nan, False
    for i in range(m):
        if pos != 0 and i >= entry_i and not imm:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        held = pos
        new = pos
        if i + 1 < m and lsig[i] and pos != 1:
            new, entry_i, s_, t_, imm = 1, i + 1, sl[i], tp[i], not ok[i]
        elif i + 1 < m and ssig[i] and pos != -1:
            new, entry_i, s_, t_, imm = -1, i + 1, sl[i], tp[i], not ok[i]
        elif imm and pos != 0 and i == entry_i:
            new, imm = 0, False                          # a level already through the close exits here
        if new == 1 and held != 1:
            le[i] = True
        elif new == -1 and held != -1:
            se[i] = True
        elif new == 0 and held == 1:
            lx[i] = True
        elif new == 0 and held == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
