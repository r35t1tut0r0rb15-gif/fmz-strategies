"""30-minute bars, from flat, on bars opening 09:30 to 14:30 UTC: the close crossing over the last pivot-high resistance (10 / 15) on a volume oscillator (EMA 5 vs 10) above 20 %, a candle without a long lower wick and the close above the EMA 150 goes long; the mirror through the pivot-low support goes short; each closes when the bar trades through a line 3.2 ATR 14 from the previous close.
Port of FMZ strategy #438379 "Support and Resistance Strategy with Volume Breakout and Trailing Stop Loss" (SUPPORT RESISTANCE STRATEGY [5MIN TF]).

FMZ source id: 438379

Source
    https://www.fmz.com/strategy/438379 (PineScript v5, FMZ last modified 2024-01-11 17:58:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 163-244), pivots 10 / 15; volume oscillator break 20; EMA 150; ATR 14 x 3.2 both sides; session 0915-1445; close_all at 14:55
    Resistance = fixnan(pivothigh(10, 15)[1]);  crossover(close, Resistance) and osc_vol > 20 and not (open - low > close - open) and opentrades == 0 and session and close >= ema(150) -> entry Long
    position_size > 0 -> exit(stop = close - 3.2 atr(14)) (re-sent every bar);  short mirror;  close_all when hour == 14 and minute == 55

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-sent every bar at the latest close minus 3.2 ATR, so it can move down as well as up:
      neither a fixed house stop nor the house trail expresses it, so the port follows it in the signals
      (a bar whose low reaches the previous bar's level closes at the next open; mark
      trailing_stop_pending). The session is read in UTC (the header exchange): bars opening 09:15 ..
      14:44, i.e. 09:30 .. 14:30 on 30-minute bars. The 14:55 close_all never meets a 30-minute bar open
      (weird case). The volume oscillator compares two volume EMAs. Pivots are strict. A position ends at
      its line or not at all; entries need no open trade. REVERSAL INTENDED (entries only from flat). No
      sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR line exits in the signals.
    2 generic: PASS, pivot support / resistance breaks on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (risk 200 input feeds a commented line).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume oscillator 100 x (ema(v, 5) - ema(v, 10)) / ema(v, 10); exchange volume to be compared later (Austin, 2026-10-23).
Session open: entries on bars opening 09:15 to 14:45 UTC (header exchange time); the 14:55 close_all never fires.
Opposite entries cannot occur (entries only from flat).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_438379_pivot_sr_break_volume_osc_atr_line_30m_flat_only"
FAMILY = "support_resistance"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [3.2, 2.0],
    "vol_break": [20, 10],
}
DEFAULT_PARAMS = {"l_bars": 10, "r_bars": 15, "vol_break": 20, "ema_len": 150, "atr_mult": 3.2}


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


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    lb, rb = int(p["l_bars"]), int(p["r_bars"])
    hh, hv_ = _pivot_hit(h, 1, lb, rb)
    lh, lv_ = _pivot_hit(lo, -1, lb, rb)
    res = _fixnan(pd.Series(np.where(hh, hv_, np.nan), index=c.index).shift(1))
    sup = _fixnan(pd.Series(np.where(lh, lv_, np.nan), index=c.index).shift(1))
    e5, e10 = v.ewm(span=5, adjust=False).mean(), v.ewm(span=10, adjust=False).mean()
    osc = 100 * (e5 - e10) / e10.where(e10 != 0)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ix = c.index
    mins = ix.hour * 60 + ix.minute
    sess = np.asarray((mins >= 9 * 60 + 15) & (mins < 14 * 60 + 45))
    vb = osc > float(p["vol_break"])
    long_c = ((c > res) & (c.shift(1) <= res.shift(1)) & vb & ~(o - lo > c - o) & (c >= ema)).to_numpy() & sess
    short_c = ((c < sup) & (c.shift(1) >= sup.shift(1)) & vb & ~(o - c < h - o) & (c <= ema)).to_numpy() & sess
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    k = float(p["atr_mult"]) * _rma(tr, 14)
    ltr, strl = (c - k).to_numpy(), (c + k).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        fresh = False
        if pend != 0:
            pos, pend, fresh = pend, 0, True
        if not fresh and i > 0:
            if pos == 1 and lv[i] <= ltr[i - 1]:
                lx[i], pos = True, 0
                continue
            if pos == -1 and hv[i] >= strl[i - 1]:
                sx[i], pos = True, 0
                continue
        if pos == 0 and pend == 0 and i + 1 < m:
            if long_c[i]:
                le[i], pend = True, 1
            elif short_c[i]:
                se[i], pend = True, -1
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
