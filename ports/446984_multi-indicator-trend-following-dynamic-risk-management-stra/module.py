"""MACD crossings in an EMA 50 / 200 trend with an RSI filter, bar size from the search, with an ATR bracket: a cross up with the close above a rising-trend EMA 50 and the RSI under 70 goes long, the mirror
goes short; stop 3 ATR(14), target 6 ATR from the signal close; reversing.
Port of FMZ strategy #446984 "Multi Indicator Trend Following Dynamic Risk Management Strategy" (EPS V6 (Enhanced Professional Strategy V6)).

FMZ source id: 446984

Source
    https://www.fmz.com/strategy/446984 (PineScript v5, FMZ last modified 2024-04-03 17:40:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-172), RSI 14; MACD 12 / 26 / 9; ATR 14, stop multiplier 3, risk : reward 2, target ratio 2; EMA 50 / 200; risk 1 % per trade
    crossover(macd, signal) and rsi < 70 and close > ema50 and ema50 > ema200 -> entry Long, exit(stop = close - 3 atr, limit = close + 6 atr), exit(limit = close + 12 atr);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. Two
      exits cover the whole position; the 6-ATR limit is always reached before the 12-ATR one, so the
      bracket is sl_stop = 3 ATR / close and tp_stop = 6 ATR / close of the signal bar, shifted one bar
      inside stops() and re-based on the fill. A repeated signal inside the trade re-issues the levels:
      not expressible (mark trailing_stop_pending); the opening levels are kept. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). The risk quantity is sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar (re-sent levels marked).
    2 generic: PASS, MACD crossings with trend and RSI filters, ATR bracket.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: the risk quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446984_macd_cross_ema50_200_trend_rsi_atr_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_mult": [3.0, 1.5],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"trail_mult": 3.0, "rr": 2.0, "atr_len": 14, "rsi_len": 14, "ema_fast": 50, "ema_slow": 200}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r < 70) & (c > ef) & (ef > es)
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r > 30) & (c < ef) & (ef < es)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["trail_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": (a * float(p["rr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
