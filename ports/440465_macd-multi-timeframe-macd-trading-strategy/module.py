"""MACD histogram zero crossings with an EMA 50 filter, 1-hour bars: the histogram crossing above zero with the close at or above the EMA 50 goes long, below zero with the close at or below it short; a
close through the Parabolic SAR or a bar reaching EMA 14 +/- 3 ATR(14) closes; a trade still losing more than 10 bars after its last signal closes; reversing.
Port of FMZ strategy #440465 "多周期MACD指标交易策略Multi-Timeframe-MACD-Trading-Strategy" (MACD+ Strategy [SA]).

FMZ source id: 440465

Source
    https://www.fmz.com/strategy/440465 (PineScript v4, FMZ last modified 2024-01-30 17:44:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 211-596), MACD 12 / 26 / 9; trend filter MA (EMA 50); trailing stop SAR (0.04 / 0.02 / 0.5); target ATR (EMA 14 +/- 3 ATR 14); timed exit on, method 3 (losing trades), 10 bars; both directions
    buySignal = crossover(MACD - signal, 0) and close >= ema50;  shortSignal = crossunder(..) and close <= ema50;  sellSignal = close <= sar or high >= ema14 + 3 atr;  coverSignal = close >= sar or low <= ema14 - 3 atr
    entry Long / Short;  close Long on sellSignal, close Short on coverSignal;  barsSinceEntry counts bars, reset by flat, entries and either exit signal;  > 10 and openprofit < 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are bar-close tests sent at the next open. The target band is recomputed every bar, as
      written. The timed exit uses only the sign of the open profit of the single position, which is
      the close against the fill price (no account-size dependence). The divergence part only feeds
      plots. A close acts only on the held position; one after a reversing entry leaves the reversal
      standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity size,
      capital and commission are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-tested SAR and band exits.
    2 generic: PASS, MACD histogram, EMA, SAR and ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity, capital and commission settings.
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

NAME = "fmz_440465_macd_hist_ema50_sar_atr_exits"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [50, 100],
    "bse": [10, 20],
}
DEFAULT_PARAMS = {"ma_length": 50, "bse": 10, "fast": 12, "slow": 26, "signal": 9, "sar_start": 0.04,
                  "sar_inc": 0.02, "sar_max": 0.5, "atr_len": 14, "tp_mult": 3.0}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar reference block: the SAR value (NaN on the first bar)."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    maf = c.ewm(span=int(p["ma_length"]), adjust=False).mean()
    L = ((delta > 0) & (delta.shift(1) <= 0) & (c >= maf)).to_numpy()
    S = ((delta < 0) & (delta.shift(1) >= 0) & (c <= maf)).to_numpy()
    hv, lv, cv, ov = (x.to_numpy(dtype=float) for x in (h, lo, c, o))
    sar = _sar(hv, lv, cv, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    n = int(p["atr_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    band = float(p["tp_mult"]) * _rma(tr, n)
    e14 = c.ewm(span=n, adjust=False).mean()
    sell = (cv <= sar) | (h >= e14 + band).to_numpy()
    cover = (cv >= sar) | (lo <= e14 - band).to_numpy()
    bse = int(p["bse"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, b, x = 0, 0, np.nan
    for i in range(m):
        b = b + 1
        if pos == 0:
            b = 0
        new = pos
        if L[i]:
            new, b = 1, 0
        if S[i]:
            new, b = -1, 0
        if sell[i]:
            if pos == 1 and new == 1:
                new = 0
            b = 0
        if cover[i]:
            if pos == -1 and new == -1:
                new = 0
            b = 0
        losing = (pos == 1 and cv[i] < x) or (pos == -1 and cv[i] > x)
        if b > bse and losing:
            new, b = 0, 0
        if new != 0 and new != pos and i + 1 < m:
            x = ov[i + 1]                                # the fill of the new position
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
