"""SMA 20 / 50 crossings filtered by the RSI 7 and the stochastic 7, 4-hour bars: the cross up with the RSI under 70 and %K under 80 goes long, the cross down with the RSI over 30 and %K over 20 goes short; reversing. The ATR bracket re-sent every bar from the bar's own high / low is not ported (pending).
Port of FMZ strategy #454352 "基于双均线交叉RSI和随机指标的短线量化交易策略-Short-term-Quantitative-Trading-Strategy-Based-on-Dual-Moving-Average-Crossover-RSI-and-Stochastic-Indicators" (Cruce de Medias con Filtros de RSI y Estocástico).

FMZ source id: 454352

Source
    https://www.fmz.com/strategy/454352 (PineScript v5, FMZ last modified 2024-06-17 15:35:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-156), SMA 20 / 50; RSI 7 (70 / 30); stochastic 7, smooth 3 (80 / 20); ATR 14; stop 1 ATR beyond the bar's low / high, target 2 ATR beyond its high / low (every bar)
    crossover(sma20, sma50) and rsi < 70 and k < 80 -> entry Compra;  crossunder and rsi > 30 and k > 20 -> entry Venta
    long: exit(stop = low - atr, limit = high + 2 atr) every bar;  short: exit(stop = high + atr, limit = low - 2 atr) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's high / low and ATR, so it moves with the
      price; stops() cannot express this: it is not ported and the module gets the mark
      trailing_stop_pending (as #438034); positions end at the opposite entry. REVERSAL INTENDED. No
      sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket pending (mark).
    2 generic: PASS, filtered SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_454352_sma20_50_cross_rsi_stoch_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
    "rsi_len": [7, 14],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "rsi_len": 7, "k_len": 7, "smooth_k": 3}


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
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["k_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = (100 * (c - ll) / rng.where(rng > 0)).rolling(int(p["smooth_k"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70) & (k < 80)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 30) & (k > 20)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
