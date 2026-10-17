"""Engulfing bars in the Supertrend direction, 1-hour bars: in an up trend (Supertrend 10 / 3), a bar closing above the open
of a red previous bar, with neither bar small-bodied, goes long with the stop at its low and the target its range plus
400 ticks above the close; the down-trend mirror goes short. Ticks re-expressed as ATR multiples.
Port of FMZ strategy #434705 "SuperTrend Engulfing Strategy" (Engulfing with Trend).

FMZ source id: 434705

Source
    https://www.fmz.com/strategy/434705 (PineScript v5, FMZ last modified 2023-12-08 15:40:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 107-201), Supertrend ATR 10 x 3 on hl2 (Wilder ATR); boring 25 %, engulfing 50 %; stop level 200 ticks
    bullEngulfing = uptrend and close[1] < open[1] and close > open[1] and not boring[1] and not (body / range <= 50 %) -> entry long
    exit(stop = low, limit = 2 (close + 200 ticks) - low) on signal bars;  shorts mirror (stop = high, limit = 2 (close - 200 ticks) - high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Supertrend is this script's (KivancOzbilgic form): bands ratcheted on the previous close,
      the trend flipped by a close beyond the previous band. A zero-range bar gives no ratio (na: not
      small).
    * The levels come from the signal bar and are ported as fractions of the signal close (stop
      (close - low) / close; target ((close - low) + 2 x 0.1 ATR) / close: 200 ticks of 0.1 on hourly
      BTC are about 0.1 x the Wilder ATR 10), shifted one bar inside stops() (re-based on the fill).
      A signal whose stop is not beyond the close places no entry. A repeated signal inside the trade
      re-issues the levels: not expressible (mark trailing_stop_pending); the opening levels are kept.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ
      = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-issued levels approximated).
    2 generic: ADAPT, tick padding -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_434705_supertrend_engulfing_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [3.0, 2.0],
    "pad_atr": [0.1, 0.5],
}
DEFAULT_PARAMS = {"atr_len": 10, "mult": 3.0, "boring": 25.0, "engulf": 50.0, "pad_atr": 0.1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    mlt = float(p["mult"])
    m = len(cv)
    up, dn = src - mlt * atr, src + mlt * atr
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        up1 = up[i - 1] if i > 0 and not np.isnan(up[i - 1]) else up[i]
        dn1 = dn[i - 1] if i > 0 and not np.isnan(dn[i - 1]) else dn[i]
        cp = cv[i - 1] if i > 0 else np.nan
        if cp > up1:
            up[i] = max(up[i], up1)
        if cp < dn1:
            dn[i] = min(dn[i], dn1)
        t1 = trend[i - 1] if i > 0 else 1
        trend[i] = 1 if (t1 == -1 and cv[i] > dn1) else (-1 if (t1 == 1 and cv[i] < up1) else t1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = np.abs(ov - cv) * 100 / np.abs(hv - lv)
        ratio[~np.isfinite(ratio)] = np.nan
        r1 = np.concatenate(([np.nan], ratio[:-1]))
        o1, cl1 = np.concatenate(([np.nan], ov[:-1])), np.concatenate(([np.nan], cv[:-1]))
        not_small = ~(r1 <= float(p["boring"])) & ~(ratio <= float(p["engulf"]))
        bull = (trend == 1) & (cl1 < o1) & (cv > o1) & not_small
        bear = (trend == -1) & (cl1 > o1) & (cv < o1) & not_small
        pad = 2 * float(p["pad_atr"]) * atr
        l_sl, s_sl = (cv - lv) / cv, (hv - cv) / cv
        le = bull & (l_sl > 0)
        se = bear & (s_sl > 0)
        sl = np.where(le, l_sl, np.where(se, s_sl, np.nan))
        tp = np.where(le, (cv - lv + pad) / cv, np.where(se, (hv - cv + pad) / cv, np.nan))
    return le, se, sl, tp


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
