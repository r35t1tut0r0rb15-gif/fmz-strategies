"""SMA 10 / 50 crossings, 3-hour bars: the cross up goes long, the cross down goes short, each with a 1.5 ATR 14 stop and target from the signal close; reversing.
Port of FMZ strategy #477598 "动态均线交叉趋势跟踪策略结合ATR风险管理系统-Dynamic-Moving-Average-Crossover-Trend-Following-Strategy-with-ATR-Risk-Management-System" (Trend-Following Strategy).

FMZ source id: 477598

Source
    https://www.fmz.com/strategy/477598 (PineScript v5, FMZ last modified 2025-01-06 16:27:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 77-136), SMA 10 / 50; ATR 14 x 1.5 stop and target; qty = equity x 200 % / close; timeframe and risk inputs unused
    crossover(sma10, sma50) -> entry Long (qty), exit(stop = close - 1.5 atr, limit = close + 1.5 atr);  crossunder -> entry Short, exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close and ATR: sent as fractions of the fill
      open; a level at or through it is marketable and closed one bar late (as #458256). The crossings
      alternate, so no repeat signal re-sends it. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The equity-based qty is sizing.
      FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, SMA crossings with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 200 % / close stored, not ported.
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

NAME = "fmz_477598_sma10_50_cross_atr15_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 3.0],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "slow": 50, "fast": 10, "atr_length": 14}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    a = _atr(bars_df, p["atr_length"]) * float(p["atr_mult"])
    lvl = {"l_sl": c - a, "l_tp": c + a, "s_sl": c + a, "s_tp": c - a}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
