"""Three-line strikes on the EMA 200 side: three red candles then a larger green engulfing candle above the EMA goes
long, the mirror below goes short, with a 1 ATR stop and a 2 ATR target, two-hour bars.
Port of FMZ strategy #482466 "三线突破趋势跟踪策略结合EMA动态过滤和ATR风险管理系统-Three-Line-Strike-Trend-Following-Strategy-with-EMA-Dynamic-Filter-and-ATR-Risk-Management-System" (3 Line Strike [TTF] - Strategy with ATR and EMA Filter).

FMZ source id: 482466

Source
    https://www.fmz.com/strategy/482466 (PineScript v5, FMZ last modified 2025-02-18 15:30:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-178), ATR 14, EMA 200
    bull = bars 1-3 red, bar 0 green with |body| > |body[1]|, and close > ema200 -> entry long with
    exit(limit = close + 2 ATR, stop = close - 1 ATR); bear mirrored -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: 1 ATR / close and 2 ATR / close, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, candle colours and sizes, an EMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482466_three_line_strike_ema200_atr_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [200, 100],
    "tp_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "ema_len": 200, "sl_mult": 1.0, "tp_mult": 2.0}


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
    o, c = bars_df["open"], bars_df["close"]
    body = c - o
    green, red = body > 0, body < 0
    bigger = body.abs() > body.shift(1).abs()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()

    def lag(s, k):
        return s.shift(k, fill_value=False)

    bull = lag(red, 1) & lag(red, 2) & lag(red, 3) & green & bigger & (c > ema)
    bear = lag(green, 1) & lag(green, 2) & lag(green, 3) & red & bigger & (c < ema)
    false = pd.Series(False, index=bars_df.index)
    return bull.astype(bool), false, bear.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
