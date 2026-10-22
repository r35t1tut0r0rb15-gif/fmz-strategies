"""Alternating RSI 14 signals, 1-hour bars: the first RSI cross over 30 after a short signal goes long, the first cross under 70 after a long signal goes short (reversing); a position closes on the bar
tests of its target, stop, trail (the 99999 inputs read as price amounts) or a 0.4 % "liquidation" level from the signal bar's open.
Port of FMZ strategy #440456 "基于RSI指标的反转交易策略An-RSI-Reversal-Trading-Strategy" (Adding some essential components to a prebuilt RSI strategy).

FMZ source id: 440456

Source
    https://www.fmz.com/strategy/440456 (PineScript v4, FMZ last modified 2024-01-30 17:06:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 179-279), RSI 14 (30 / 70); trailing stop, take profit, stop loss 99999 / 100 (price units); leverage 200
    long_signal = crossover(last long time, last short time);  short_signal mirrored;  entry Long / Short on them;  open price of the signal bar kept;  last_high / last_low since the signal
    close Long when low <= open x (1 - (0.8 + 0.2 / 200) / 200), high >= open + 999.99, low <= open - 999.99, or high <= last_high - 999.99 (shorts mirrored, 0.78)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the trail, target and stop inputs (99999 / 100 = 999.99) are price amounts; the port
      uses fractions at the BTC reading near 42000 (0.0238 of the signal open or of the best high /
      low); the second grid value moves them out of reach. The liquidation levels are fractions of the
      signal bar's open already (0.4005 % long, 0.3905 % short). All exits are bar tests sent at the next
      open; a close acts only on the held position, and the reversal on a signal bar stands (as #438020).
      The signals alternate (a signal only after the opposite one). The leverage input only sets the
      liquidation level. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-tested levels.
    2 generic: ADAPT, price-unit levels -> fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (leverage sets the liquidation level only).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND431415 (2 members, best partner #431415, Jaccard 0.786); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440456_rsi_alternating_liquidation_exits"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level_frac": [0.0238, 0.5],
    "length": [14, 7],
}
DEFAULT_PARAMS = {"level_frac": 0.0238, "length": 14, "oversold": 30, "overbought": 70, "leverage": 200}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    r = _rsi(bars_df["close"], int(p["length"]))
    os_, ob = float(p["oversold"]), float(p["overbought"])
    lg = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    sh = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    f = float(p["level_frac"])
    lev = float(p["leverage"])
    lq_l = (0.8 + 0.2 * (1 / lev)) / lev
    lq_s = (0.78 + 0.2 * (1 / lev)) / lev
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    last_l = last_s = -1
    sig_l = sig_s = -1
    ol = os_open = 0.0
    hi = lw = np.nan
    for i in range(m):
        pl, ps = last_l, last_s
        if lg[i]:
            last_l = i
        if sh[i]:
            last_s = i
        lsig = last_l > last_s and pl <= ps
        ssig = last_s > last_l and ps <= pl
        if lsig:
            ol, sig_l = o[i], i
        if ssig:
            os_open, sig_s = o[i], i
        in_l, in_s = sig_l > sig_s, sig_s > sig_l
        hi = np.nan if not in_l else (h[i] if (np.isnan(hi) or h[i] > hi) else hi)
        lw = np.nan if not in_s else (lo[i] if (np.isnan(lw) or lo[i] < lw) else lw)
        x_l = (lo[i] <= ol * (1 - lq_l) or h[i] >= ol * (1 + f) or lo[i] <= ol * (1 - f)
               or (not np.isnan(hi) and h[i] <= hi * (1 - f)))
        x_s = (h[i] >= os_open * (1 + lq_s) or lo[i] <= os_open * (1 - f) or h[i] >= os_open * (1 + f)
               or (not np.isnan(lw) and lo[i] >= lw * (1 + f)))
        new = pos
        if lsig:
            new = 1
        if ssig:
            new = -1
        if x_l and pos == 1 and new == 1:
            new = 0
        if x_s and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
