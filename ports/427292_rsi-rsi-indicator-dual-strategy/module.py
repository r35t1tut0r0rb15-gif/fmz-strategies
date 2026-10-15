"""4All V3, RSI(4) extremes: RSI crossing under 5 goes long, crossing over 95 goes short; a position
is closed at a take-profit or stop-loss distance from the OPEN of the bar that started the signal
(tested on each completed bar's high / low, filled at the next open).
Port of FMZ strategy #427292 "RSI Indicator Dual Strategy".

FMZ source id: 427292

Source
    https://www.fmz.com/strategy/427292 (PineScript v3, FMZ last modified 2023-09-19 19:43:19).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 166-287), RSI 4, band 5, TS 99999 / 10000, TP 15 / 10000,
SL 23 / 10000, pyramiding input 1, leverage 1
    long = crossunder(rsi, 5); short = crossover(rsi, 95)
    long_signal = the first long after a short (crossover of the last-long / last-short times);
    ref = open of the long_signal bar (short mirrors)
    exits: high >= ref + tp | low <= ref - sl | low <= liquidation(ref, leverage) | trailing (ts)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: tp / sl are price units (15 / 23 ten-thousandths, i.e. pips on an FX pair).
      They become tp_atr / sl_atr x Wilder ATR(14) taken on the signal bar.
    * The exits are tests on the completed bar's high / low sent as strategy.close orders, so they
      are exit signals filled at the next open (rule 3), not stops.
    * The trailing distance 99999 / 10000 is the author's "off" value: not ported. The liquidation
      exits depend on leverage (sizing): with the default leverage 1 the long one is at a price of 0
      and the short one at +98 %; not ported (stored in original_sizing.txt).
    * pyramiding input 1: each RSI signal counts (sectionLongs >= 1).
    * strategy.entry reverses: REVERSAL INTENDED; the opposite entry wins over a same-bar close.
      The window function testPeriod() is the constant true.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and bar-close exit tests.
    2 generic: ADAPT, price-unit tp / sl -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: leverage / liquidation and trailing inputs stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427292_4all_v3_rsi_extremes"
FAMILY = "rsi_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_band": [5, 10],
    "tp_atr": [1.0, 2.0],
    "sl_atr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"rsi_length": 4, "rsi_band": 5, "tp_atr": 1.0, "sl_atr": 1.5, "atr_length": 14}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n).to_numpy()


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    r1 = np.concatenate(([np.nan], r[:-1]))
    lo_b, hi_b = float(p["rsi_band"]), 100.0 - float(p["rsi_band"])
    long_c = (r < lo_b) & (r1 >= lo_b)          # crossunder(rsi, ln)
    short_c = (r > hi_b) & (r1 <= hi_b)         # crossover(rsi, sn)
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    atr = _atr(bars_df, int(p["atr_length"]))
    m = len(o)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    last_long = last_short = 0                  # bar numbers of the last long / short condition (0 = none)
    ref_l = ref_s = np.nan                      # open of the last long / short signal bar
    tp_l = sl_l = tp_s = sl_s = np.nan
    for i in range(m):
        prev_l, prev_s = last_long, last_short
        if long_c[i]:
            last_long = i + 1
        if short_c[i]:
            last_short = i + 1
        if last_long > last_short and prev_l <= prev_s:        # long_signal
            ref_l, tp_l, sl_l = o[i], p["tp_atr"] * atr[i], p["sl_atr"] * atr[i]
        if last_short > last_long and prev_s <= prev_l:        # short_signal
            ref_s, tp_s, sl_s = o[i], p["tp_atr"] * atr[i], p["sl_atr"] * atr[i]
        exit_l = pos == 1 and (h[i] >= ref_l + tp_l or lo[i] <= ref_l - sl_l)
        exit_s = pos == -1 and (lo[i] <= ref_s - tp_s or h[i] >= ref_s + sl_s)
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif exit_l or exit_s:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
