"""Closes crossing the SMMA 17, always in, with a stop 0.75 ATR beyond the SMMA and a fixed target (1150 / 1500 points
on the author's BTC_USDT, read as 1.2 / 1.5 ATR), four-hour bars.
Port of FMZ strategy #482592 "Dual-Direction-SMMA-Crossover-Strategy-with-ATR-Based-Risk-Management-and-Fixed-Take-Profit-双向SMMA交叉ATR风控定向获利策略" (SMMA 17 Crossover Strategy (Long & Short, ATR SL & Fixed TP)).

FMZ source id: 482592

Source
    https://www.fmz.com/strategy/482592 (PineScript v5, FMZ last modified 2025-02-19 10:59:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 92-151), SMMA 17, ATR 14 (rma of tr(true)), stop 0.75 ATR
    crossover(close, smma) -> entry long, TP = close + 1150; every bar: exit(stop = smma - 0.75 ATR, limit = TP)
    crossunder(close, smma) -> close long, entry short, TP = close - 1500; every bar: exit(stop = smma + 0.75 ATR)
    crossover -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes repeat the reversal the entries make: always in after the first cross (REVERSAL INTENDED).
    * The stop is re-issued every bar from the current SMMA and ATR (a moving level): fixed at the entry as
      (close - smma + 0.75 ATR) / close of the signal bar (shorts mirrored), shifted one bar inside stops() and
      re-based on the fill; mark trailing_stop_pending.
    * The 1150 / 1500-point targets are price units (criterion 2): ATR multiples judged on the author's BTC_USDT
      4-hour bars of 2024-25 (ATR about 900-1000): 1.2 ATR long, 1.5 ATR short, from the signal bar (as #489333).
    * Stop module: portfolio_kwargs {} (D4). FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, an SMMA and ATR multiples (the point targets converted).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482592_smma17_cross_atr_stop_atr_target"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_atr": [0.75, 1.5],
    "smma_len": [17, 34],
}
DEFAULT_PARAMS = {"smma_len": 17, "atr_len": 14, "stop_atr": 0.75, "tp_long_atr": 1.2, "tp_short_atr": 1.5}


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
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # ta.tr(true): the first true range is high - low
    return _rma(tr, n)


def _parts(bars_df, p):
    c = bars_df["close"]
    smma = _rma(c, int(p["smma_len"]))       # na(smma[1]) ? sma : recursive = Pine rma
    atr = _atr(bars_df, int(p["atr_len"]))
    long_e = ((c > smma) & (c.shift(1) <= smma.shift(1))).astype(bool)
    short_e = ((c < smma) & (c.shift(1) >= smma.shift(1))).astype(bool)
    sl = ((c - smma + p["stop_atr"] * atr) / c).where(long_e, (smma + p["stop_atr"] * atr - c) / c)
    tp = (p["tp_long_atr"] * atr / c).where(long_e, p["tp_short_atr"] * atr / c)
    return long_e, short_e, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _parts(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _parts(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
