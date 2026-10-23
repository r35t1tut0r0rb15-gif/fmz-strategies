"""Squeeze momentum (BB 85 x 2.1 vs KC 38 x 2, linear-regression value positive and rising, outside a no-squeeze state), a volume-weighted RSI 22 over 45 and the SAR 0.73 / 0.5 / 0.06 below the close, hourly bars: the first bullish set after a bearish one goes long, the first bearish set after a bullish one goes short; reversing.
Port of FMZ strategy #431218 "Dual Laser Trend seeking Strategy" (M-SQUEEZE).

FMZ source id: 431218

Source
    https://www.fmz.com/strategy/431218 (PineScript v4, FMZ last modified 2023-11-06 10:01:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 264-397), squeeze BB 85 / 2.1, KC 38 / 2; SAR 0.73 / 0.5 / 0.06; RSI volume weighted 22, centre 45; window 2018 .. 2222
    longCond = VAL > 0 and VAL > nz(VAL[1]) and not NOSQZ and RSI_V > 45 and SAR < close;  shortCond mirror
    longCondition0 = longCond and CondIni0[1] == -1 -> entry Long;  shortCondition0 = shortCond and CondIni0[1] == 1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The alternation state starts at 0, so the very first set of either side does not trade, as written.
      NOSQZ is "neither squeeze on nor off". The SAR maximum (0.06) is under its 0.73 start, so the step
      falls to 0.06 after the first new extreme, as Pine's sar does. The volume-weighted RSI averages start
      from the first bar (WiMA). The author's window is dropped. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, squeeze momentum with volume RSI and SAR agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume-weighted RSI 22; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2018 .. 2222 window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431218_squeeze_momentum_volume_rsi_sar_alternating_reversal"
FAMILY = "squeeze_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [85, 20],
    "kc_length": [38, 20],
}
DEFAULT_PARAMS = {"bb_length": 85, "kc_length": 38, "bb_mult": 2.1, "kc_mult": 2.0, "sst": 0.73, "sinc": 0.5,
                  "smax": 0.06, "rsi_len": 22, "rsi_obos": 45.0}


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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def _wima(x, n):
    """The source's WiMA: (src + nz(prev x (n - 1))) / n, from the first bar."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = (v[i] + (0.0 if np.isnan(prev) else prev * (n - 1))) / n
        prev = out[i]
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    nb, nk = int(p["bb_length"]), int(p["kc_length"])
    basis, dev = c.rolling(nb).mean(), float(p["bb_mult"]) * c.rolling(nb).std(ddof=0)
    ub, lb = basis + dev, basis - dev
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    ma, rma_ = c.rolling(nk).mean(), tr.rolling(nk).mean()
    uk, lk = ma + rma_ * float(p["kc_mult"]), ma - rma_ * float(p["kc_mult"])
    sqz_on = (lb > lk) & (ub < uk)
    sqz_off = (lb < lk) & (ub > uk)
    nosqz = ~sqz_on & ~sqz_off
    val = _linreg(c - ((h.rolling(nk).max() + lo.rolling(nk).min()) / 2 + c.rolling(nk).mean()) / 2, nk)
    v1 = val.shift(1).fillna(0.0)
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sst"]), float(p["sinc"]), float(p["smax"])), index=c.index)
    d = c.diff()
    up = (d.abs() * v).where(d > 0, 0.0)
    dn = (d.abs() * v).where(d < 0, 0.0)
    n = int(p["rsi_len"])
    ut, dt = _wima(up, n), _wima(dn, n)
    rsi_v = 100 * (ut / (ut + dt))
    ob = float(p["rsi_obos"])
    lc = ((val > 0) & (val > v1) & ~nosqz & (rsi_v > ob) & (sar < c)).to_numpy()
    sc = ((val < 0) & (val < v1) & ~nosqz & (rsi_v < ob) & (sar > c)).to_numpy()
    m = len(lc)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ci = 0
    for i in range(m):
        le[i] = lc[i] and ci == -1
        se[i] = sc[i] and ci == 1
        ci = 1 if lc[i] else (-1 if sc[i] else ci)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
