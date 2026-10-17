"""Breakouts of the 09:30 five-minute opening candle with a stop beyond the candle by 1 ATR and a 1.5-range target,
5-minute bars: the close crossing above the opening candle's high goes long; crossing below its low goes short.
Port of FMZ strategy #482863 "五分钟开盘突破ATR动态止盈止损量化交易策略-Five-Minute-Opening-Breakout-Strategy-with-Dynamic-ATR-Based-Stop-Loss-and-Take-Profit" (5-Min Open Candle Breakout).

FMZ source id: 482863

Source
    https://www.fmz.com/strategy/482863 (PineScript v5, FMZ last modified 2025-02-27 17:33:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-145), SL 1 ATR(14), TP 1.5 x range
    first candle = the bar starting at timestamp(year, month, dayofmonth, 9, 30) (chart time zone): its high / low kept
    (var) until the next first candle; long = crossover(close, high0); short = crossunder(close, low0)
    exit(stop = low0 - ATR, limit = high0 + 1.5 (high0 - low0)) (short mirrored), every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (check 9 / C6): timestamp() without a zone uses the chart's exchange zone, UTC on the author's Binance
      chart, so the opening candle is 09:30 UTC as written (session_tz "UTC", the default); the NYSE open the comment
      names is the variant (session_tz "America/New_York", DST by the zone).
    * The stop moves with the current ATR (re-issued every bar): fixed at the entry as the signal bar's distances,
      sl = (close - (low0 - ATR)) / close and tp = (high0 + 1.5 range - close) / close (short mirrored), shifted one bar
      inside stops() and re-based on the fill; mark trailing_stop_pending. A signal with a level on the wrong side of
      the close emits no entry (as #490798).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "5min" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, an opening range and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:30 in session_tz (UTC as written; America/New_York, DST by the zone, as the variant): the 5-minute
    opening candle.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482863_opening_candle_breakout_atr_range_bracket"
FAMILY = "opening_range_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "session_tz": ["UTC", "America/New_York"],
    "tp_factor": [1.5, 1.0],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "sl_factor": 1.0, "tp_factor": 1.5, "atr_len": 14}


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


def _var_level(x):
    """A Pine `var` level: the last value set, kept until the next one (past values only)."""
    v = x.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    loc = bars_df.index.tz_convert(p["session_tz"])
    first = pd.Series((loc.hour == 9) & (loc.minute == 30), index=c.index)
    hi0 = _var_level(h.where(first))
    lo0 = _var_level(lo.where(first))
    atr = _atr(bars_df, int(p["atr_len"]))
    rng = hi0 - lo0
    sl_l = (c - (lo0 - p["sl_factor"] * atr)) / c
    tp_l = (hi0 + p["tp_factor"] * rng - c) / c
    sl_s = ((hi0 + p["sl_factor"] * atr) - c) / c
    tp_s = (c - (lo0 - p["tp_factor"] * rng)) / c
    long_e = ((c > hi0) & (c.shift(1) <= hi0.shift(1)) & (sl_l > 0) & (tp_l > 0)).astype(bool)
    short_e = ((c < lo0) & (c.shift(1) >= lo0.shift(1)) & (sl_s > 0) & (tp_s > 0)).astype(bool)
    return long_e, short_e, sl_l.where(long_e, sl_s), tp_l.where(long_e, tp_s)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _signals(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
