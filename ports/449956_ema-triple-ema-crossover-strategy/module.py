"""EMA 10 / 50 crossings confirmed by the EMA 25, 1-hour bars, with an ATR bracket: a cross up with the EMA 25 above the EMA 50 goes long, the mirror goes short; stop 3 ATR(14), target 6 ATR from the
signal close; reversing.
Port of FMZ strategy #449956 "三重EMA交叉策略Triple-EMA-Crossover-Strategy" (Triple EMA Crossover Strategy).

FMZ source id: 449956

Source
    https://www.fmz.com/strategy/449956 (PineScript v5, FMZ last modified 2024-04-30 16:34:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-144), EMA 10 / 25 / 50; ATR 14, risk multiplier 3 (target 2 x); 10 % of equity
    crossover(ema10, ema50) and ema25 > ema50 -> entry Long, exit(stop = close - 3 atr, limit = close + 6 atr);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and ATR: sl_stop = 3 ATR / close, tp_stop =
      6 ATR / close, shifted one bar inside stops() and re-based on the fill. A repeated crossing
      inside the trade re-issues the levels: not expressible (mark trailing_stop_pending). strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity
      size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar (re-sent levels marked).
    2 generic: PASS, EMA crossings with a middle-EMA filter, ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_449956_triple_ema_cross_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_mult": [3.0, 1.5],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"risk_mult": 3.0, "slow": 50, "fast": 10, "medium": 25, "atr_len": 14}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    mdl = c.ewm(span=int(p["medium"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (mdl > s)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (mdl < s)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["risk_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": (2 * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
