"""EMA 10 / 30 crosses gated by a momentum / volatility / EMA 20-50 confirmation, with a 2 ATR stop and a 3 R target,
1-hour bars: EMA 10 crossing above EMA 30 while the confirmation holds (10-bar momentum > 0, stdev 20 above its 50-bar
mean, EMA 20 > EMA 50) goes long; EMA 10 crossing below EMA 30 while it does NOT hold goes short.
Port of FMZ strategy #483115 "量子精确多指标趋势交叉交易策略-Quantum-Precision-Multi-Indicator-Trend-Crossover-Trading-Strategy" (Quantum Precision Forex Strategy).

FMZ source id: 483115

Source
    https://www.fmz.com/strategy/483115 (PineScript v5, FMZ last modified 2025-02-21 14:13:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 109-135), ATR 14 x 2, RR 3, momentum 10
    confirmation = mom(close, 10) > 0 and stdev(close, 20) > sma(stdev(close, 20), 50) and ema20 > ema50
    long = confirmation and crossover(ema10, ema30); short = not confirmation and crossunder(ema10, ema30)
    entry + exit(stop = close -+ 2 ATR, limit = close +- 6 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = atr_mult x ATR / close, tp_stop = rr x sl_stop, shifted one bar
      inside stops() and re-based on the fill (house rule). A same-side signal while held re-places it: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * The short needs the confirmation to be false, as written (asymmetric). ta.stdev is the population standard
      deviation. The linreg / correlation lines only feed plots.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header
      ("Forex" in the title is a label).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, momentum, standard deviation and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483115_ema10_30_confirmation_gate_atr_rr"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.0, 1.5],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "atr_mult": 2.0, "rr": 3.0, "mom_len": 10}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mom = c - c.shift(int(p["mom_len"]))
    sd = c.rolling(20).std(ddof=0)
    vol = sd > sd.rolling(50).mean()
    trend = c.ewm(span=20, adjust=False).mean() > c.ewm(span=50, adjust=False).mean()
    conf = (mom > 0) & vol & trend
    e10, e30 = c.ewm(span=10, adjust=False).mean(), c.ewm(span=30, adjust=False).mean()
    long_e = (conf & (e10 > e30) & (e10.shift(1) <= e30.shift(1))).astype(bool)
    short_e = (~conf & (e10 < e30) & (e10.shift(1) >= e30.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
