"""Two-hour bars: CCI 5 under -75 with the low under the lower Keltner line (SMA 30 of hlc3 - 0.7 x ATR 30) and RSI 30 under 60 goes long, the mirror short, each at most once until the script's own flag for that side is cleared by its CCI exit (over 0 for longs, under 0 for shorts); reversing.
Port of FMZ strategy #451530 "CCIRSIKC趋势滤波多空双向交易策略-CCIRSIKC-Trend-Filter-Bi-Directional-Trading-Strategy" (CCI Strategy with Trend Filter AUDNZD, GBPNZD).

FMZ source id: 451530

Source
    https://www.fmz.com/strategy/451530 (PineScript v5, FMZ last modified 2024-05-15 16:56:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 103-190), trend filter OFF; KC 30 x 0.7; CCI 5, 75 / -75; RSI 30, 60 / 60; volume multiplier 0; isLongOpen / isShortOpen flags
    longCondition = cci < -75 and low < lowerChannel and rsi < 60 and volume > sma(volume, 50) x 0 and not isLongOpen -> entry Long, isLongOpen := true;  short mirror with isShortOpen
    cci > 0 and isLongOpen -> close Long, isLongOpen := false;  cci < 0 and isShortOpen -> close Short, isShortOpen := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags are the script's own: a short entry reverses a long without clearing isLongOpen, so a
      later long needs the long's CCI exit first, as written (weird case). With the volume multiplier at
      0 the volume test is volume > 0. A close acts only on a position the bar's entries leave unchanged.
      The same rules as #442944 on 2-hour bars, with the flags. REVERSAL INTENDED. Cash order size and
      commission are sizing and costs. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Keltner-band extremes confirmed by CCI and RSI, CCI zero-line exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): cash 50000 per order, commission 0.0005, slippage 2, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) only as volume > 0 x its SMA 50 (any bar with volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451530_keltner_cci5_rsi30_flagged_entries_2h_reversal"
FAMILY = "keltner_channel"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kc_mult": [0.7, 1.5],
    "cci_len": [5, 14],
}
DEFAULT_PARAMS = {"kc_len": 30, "kc_mult": 0.7, "cci_len": 5, "cci_ob": 75.0, "cci_os": -75.0, "rsi_len": 30,
                  "rsi_ob": 60.0, "rsi_os": 60.0, "vol_mult": 0.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _cci(x, n):
    sma = x.rolling(n).mean()
    mad = pd.Series(np.nan, index=x.index)
    if len(x) >= n:
        win = np.lib.stride_tricks.sliding_window_view(x.to_numpy(dtype=float), n)
        mad.iloc[n - 1:] = np.abs(win - win.mean(axis=1, keepdims=True)).mean(axis=1)
    return (x - sma) / (0.015 * mad).where(mad != 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["kc_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    mid = ((h + lo + c) / 3).rolling(n).mean()
    rng = float(p["kc_mult"]) * _rma(tr, n)
    upper, lower = mid + rng, mid - rng
    cci = _cci(c, int(p["cci_len"]))
    rsi = _rsi(c, int(p["rsi_len"]))
    vol_ok = v > v.rolling(50).mean() * float(p["vol_mult"])
    lg = ((cci < float(p["cci_os"])) & (lo < lower) & (rsi < float(p["rsi_os"])) & vol_ok).to_numpy()
    sh = ((cci > float(p["cci_ob"])) & (h > upper) & (rsi > float(p["rsi_ob"])) & vol_ok).to_numpy()
    xl, xs = (cci > 0).to_numpy(), (cci < 0).to_numpy()
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, f_l, f_s = 0, False, False
    for i in range(m):
        new = pos
        go_l = lg[i] and not f_l
        go_s = sh[i] and not f_s
        if go_l:
            f_l = True
            if new != 1:
                new = 1
        if go_s:
            f_s = True
            if new != -1:
                new = -1
        close_l = xl[i] and f_l
        close_s = xs[i] and f_s
        if close_l:
            f_l = False
        if close_s:
            f_s = False
        if new == pos:
            if pos == 1 and close_l:
                new = 0
            elif pos == -1 and close_s:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
