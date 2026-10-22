"""RSI 2 hooks out of extremes against the EMA 50 / 100 / 200 stack, 10-minute bars: after an RSI 14 under 31, an RSI 2 cross over 10 with the EMAs stacked down goes long; after an RSI 14 over 69, an RSI 2 cross under 90 with the EMAs stacked up goes short; reversing. A long closes when RSI 14 > 69 and RSI 2 > 90 with the close over its entry price, a short on the mirror.
Port of FMZ strategy #473945 "多重RSI-EMA动量对冲增仓策略-Multi-RSI-EMA-Momentum-Hedging-Strategy-with-Position-Scaling" (Custom RSI EMA Strategy Hedge).

FMZ source id: 473945

Source
    https://www.fmz.com/strategy/473945 (PineScript v5, FMZ last modified 2024-12-04 15:41:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-241), RSI 14 / 2; EMA 50 / 100 / 200; leverage 20; size equity x 20 / close, doubled on repeat entries
    rsi14[1] < 31 and crossover(rsi2, 10) and ema50 < ema100 < ema200 -> entry Long;  rsi14[1] > 69 and crossunder(rsi2, 90) and ema50 > ema100 > ema200 -> entry Short;  rsi14 > 69 and rsi2 > 90 and long avg < close -> close Long;  rsi14 < 31 and rsi2 < 10 and short avg > close -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "average price" is the open trade's fill price (one entry per side: pyramiding 1 ignores
      repeat entries, so the doubled size never fills); a loop follows the position and its fill open
      for the close tests. The entry and close tests cannot hold on one bar (RSI 2 cannot be both just
      over 10 and over 90). Same rules as #473361 (same author; the "hedge" version only resets the
      stored average differently and draws RSI boxes, which feed no order), on 10-minute bars (rule 7).
      The size from equity and leverage is not ported. REVERSAL INTENDED. FREQ = "10min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI 2 hooks in a counter-trend EMA stack, with an RSI exit above the entry price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: equity and leverage size stored, not ported (repeat entries blocked by pyramiding 1).
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473945_rsi2_hook_ema_stack_rsi_exit_above_entry_reversal_10min"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    o, c = bars_df["open"], bars_df["close"]
    r14, r2 = _rsi(c, 14), _rsi(c, 2)
    e50, e100, e200 = (c.ewm(span=n, adjust=False).mean() for n in (50, 100, 200))
    lc = ((r14.shift(1) < 31) & (r2 > 10) & (r2.shift(1) <= 10) & (e50 < e100) & (e100 < e200)).to_numpy()
    sc = ((r14.shift(1) > 69) & (r2 < 90) & (r2.shift(1) >= 90) & (e50 > e100) & (e100 > e200)).to_numpy()
    tl = ((r14 > 69) & (r2 > 90)).to_numpy()
    ts = ((r14 < 31) & (r2 < 10)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, avg = 0, 0, np.nan
    for i in range(m):
        if nxt != pos:
            pos = nxt
            avg = ov[i] if pos != 0 else np.nan     # the fill price of the new position
        if lc[i] and pos != 1:
            le[i], nxt = True, 1
        elif sc[i] and pos != -1:
            se[i], nxt = True, -1
        if pos == 1 and nxt == 1 and tl[i] and avg < cv[i]:
            lx[i], nxt = True, 0
        elif pos == -1 and nxt == -1 and ts[i] and avg > cv[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(x, index=ix) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
