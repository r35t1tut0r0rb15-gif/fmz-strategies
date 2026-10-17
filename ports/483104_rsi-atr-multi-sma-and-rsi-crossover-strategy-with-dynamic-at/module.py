"""One bar crossing above four SMA bands (20 / 50 SMAs of highs and lows) while RSI 7 crosses 50, long only, with a
1.5 ATR stop / 2.5 ATR target, 1-hour bars.
Port of FMZ strategy #483104 "多重均线与RSI交叉动态ATR止盈止损策略-Multi-SMA-and-RSI-Crossover-Strategy-with-Dynamic-ATR-based-Take-Profit-and-Stop-Loss" (Virat Bharat Auto Trade).

FMZ source id: 483104

Source
    https://www.fmz.com/strategy/483104 (PineScript v5, FMZ last modified 2025-02-21 13:44:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-144), SMA 20 / 50 of highs and lows, RSI 7 / 50, ATR 14, SL 1.5, TP 2.5
    buy = crossover(close, sma(high, 20)) and crossover(close, sma(low, 20)) and crossover(close, sma(high, 50)) and
    crossover(close, sma(low, 50)) and crossover(rsi7, 50)
    entry + exit(loss = 1.5 ATR, profit = 2.5 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * loss / profit are ticks given ATR price distances: read as price distances (as #427592), measured from the entry:
      sl_stop = sl_mult x ATR / close, tp_stop = tp_mult x ATR / close of the signal bar, shifted one bar inside
      stops() and re-based on the fill (house rule). A buy signal while held re-places them: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * All five crosses on one bar, as written (a rare, wide bar). Long only; the source has no shorts.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages of highs and lows, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483104_four_sma_band_cross_rsi7_atr_bracket"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.0],
    "tp_mult": [2.5, 4.0],
}
DEFAULT_PARAMS = {"len20": 20, "len50": 50, "rsi_len": 7, "rsi_level": 50.0, "atr_len": 14,
                  "sl_mult": 1.5, "tp_mult": 2.5}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n1, n2 = int(p["len20"]), int(p["len50"])
    rsi = _rsi(c, int(p["rsi_len"]))
    lvl = pd.Series(p["rsi_level"], index=c.index)
    buy = (_xover(c, h.rolling(n1).mean()) & _xover(c, lo.rolling(n1).mean()) & _xover(c, h.rolling(n2).mean())
           & _xover(c, lo.rolling(n2).mean()) & _xover(rsi, lvl)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
