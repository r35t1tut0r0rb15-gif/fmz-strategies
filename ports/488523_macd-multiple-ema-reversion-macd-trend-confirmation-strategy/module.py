"""EMA ribbon pull-back with a MACD cross and a 5 ATR / 1.5 R bracket, 1-hour bars: with EMA 20 above EMA 250 and the
EMA 2 between EMA 300 (above it) and EMA 100 (below it), a MACD cross above its signal goes long; mirrored for
shorts; each trade has a 5 ATR stop and a target 1.5 times as far.
Port of FMZ strategy #488523 "多重均线回归MACD趋势确认策略-Multiple-EMA-Reversion-MACD-Trend-Confirmation-Strategy" (Price Near 200 EMA).

FMZ source id: 488523

Source
    https://www.fmz.com/strategy/488523 (PineScript v5, FMZ last modified 2025-03-28 15:40:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 140-194), EMA 20 / 250 / 2 / 100 / 300, MACD 12 / 26 / 9, ATR 14 x 5, RR 1.5
    bullishEntry = ema20 > ema250 and ema2 > ema300 and ema2 < ema100 and crossover(macd, signal)
    bearishEntry = ema20 < ema250 and ema2 < ema300 and ema2 > ema100 and crossunder(macd, signal)
    entry + exit(stop = close -+ 5 ATR, limit = close +- 1.5 x 5 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = atr_mult x ATR / close, tp_stop = rr x that, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * A same-side signal while held is ignored as an entry but its strategy.exit re-places the bracket from the new
      bar: mark trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, EMAs, MACD and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488523_ema_ribbon_macd_atr_bracket"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [5.0, 3.0],
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"ema1": 20, "ema2": 250, "ema3": 2, "ema4": 100, "ema5": 300, "macd_fast": 12, "macd_slow": 26,
                  "macd_signal": 9, "atr_len": 14, "atr_mult": 5.0, "rr": 1.5}


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
    e = {k: c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema1", "ema2", "ema3", "ema4", "ema5")}
    macd = (c.ewm(span=int(p["macd_fast"]), adjust=False).mean()
            - c.ewm(span=int(p["macd_slow"]), adjust=False).mean())
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    x_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    x_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    long_e = ((e["ema1"] > e["ema2"]) & (e["ema3"] > e["ema5"]) & (e["ema3"] < e["ema4"]) & x_up).astype(bool)
    short_e = ((e["ema1"] < e["ema2"]) & (e["ema3"] < e["ema5"]) & (e["ema3"] > e["ema4"]) & x_dn).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
