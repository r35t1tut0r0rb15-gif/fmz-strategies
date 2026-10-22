"""SMA 15 / 45 crossings on the side of the SMA 100 with the MACD's sign, 1-hour bars, with an ATR bracket: a cross up above the SMA 100 with the MACD over its signal goes long, a cross down under it with
the MACD under its signal goes short; stop 3 ATR, target 6 ATR from the signal close; reversing.
Port of FMZ strategy #445467 "基于动态多均线与MACD指标的XAUUSD交易策略Dynamic-Multi-SMA-and-MACD-based-XAUUSD-Trading-Strategy" (Refined XAUUSD SMA and MACD Strategy).

FMZ source id: 445467

Source
    https://www.fmz.com/strategy/445467 (PineScript v5, FMZ last modified 2024-03-19 17:34:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-172), SMA 100 / 15 / 45; MACD 12 / 26 / 9; ATR 14, stop 3 ATR, target 6 ATR; 10 % of equity
    close > sma100 and crossover(sma15, sma45) and macd - signal > 0 -> entry Long, exit(stop = close - 3 atr, limit = close + 6 atr);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and ATR: sl_stop = 3 ATR / close and tp_stop
      = 6 ATR / close, shifted one bar inside stops() and re-based on the fill. A repeated signal inside
      the trade re-issues the levels: not expressible (mark trailing_stop_pending); the opening levels
      are kept. XAUUSD is in the title only; the rules are generic. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar (re-sent levels marked).
    2 generic: PASS, SMA crossings with trend and MACD filters, ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only; XAUUSD in the title only).
    4 signals only: the 10 % of equity size stored.
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

NAME = "fmz_445467_sma15_45_cross_trend_macd_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [3.0, 1.5],
    "trend_len": [100, 200],
}
DEFAULT_PARAMS = {"atr_mult": 3.0, "trend_len": 100, "fast": 15, "slow": 45, "atr_len": 14, "rr": 2.0}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    t = c.rolling(int(p["trend_len"])).mean()
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    d = macd - macd.ewm(span=9, adjust=False).mean()
    f1, s1 = f.shift(1), s.shift(1)
    le = (c > t) & (f > s) & (f1 <= s1) & (d > 0)
    se = (c < t) & (f < s) & (f1 >= s1) & (d < 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": (a * float(p["rr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
