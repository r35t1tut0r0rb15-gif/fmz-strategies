"""Dual EMA ribbons, 1-hour bars, long only (the default order type): when the fast ribbon (EMA 5 / 25), the slow ribbon (EMA 28 / 72) and their centre gap have each widened upward for two bars, the
first such bar goes long; a 3 % trail behind the best body high, or a 1 % pull-back once 3 % up, closes (bar tests on the candle bodies, as the Renko option is on).
Port of FMZ strategy #440458 "Dual Moving Average Confluence Strategy" ([BT]DualRibbons R0.12).

FMZ source id: 440458

Source
    https://www.fmz.com/strategy/440458 (PineScript v3, FMZ last modified 2024-01-30 17:13:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 283-755), ribbons EMA 5 / 25 and EMA 28 / 72; Renko option on (bodies for high / low); LongsOnly; trailing stop 3 %; target 3 % with 1 % trailing profit; stop loss off; start 2018
    xup / fup / sup = bars the ribbon gaps have been positive and widening;  buy = first bar of xup >= 2 and sup >= 2 and fup >= 2;  bsState -> 1 on buy, -1 on sell;  longCondition = bsState changed to 1
    last_high = best body high since the long condition;  long_ts = body low <= last_high x 0.97;  long_tp = last_high >= entry close x 1.03 and body low <= last_high x 0.99;  close Long on the first such bar;  resets after a close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "IS This a RENKO Chart" input defaults to true, so the highs and lows are the candle bodies
      (max / min of open and close), as written. The order type defaults to LongsOnly: sells only move
      the state. The trail and target are bar tests on the signal-time state (from the long condition,
      priced at its close), sent at the next open; a close fires only on the first bar of a close run,
      and it resets the state so that the next buy can start a new long. An entry while long only resets
      the state, as written. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-tested trail and target.
    2 generic: PASS, EMA ribbon gaps.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440458_dual_ema_ribbons_long_trail"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ts": [0.03, 0.05],
    "tp": [0.03, 0.06],
}
DEFAULT_PARAMS = {"ts": 0.03, "tp": 0.03, "ttp": 0.01, "f1": 5, "f2": 25, "s1": 28, "s2": 72}


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


def _streak(gap, up):
    """Bars the gap has been positive and widening (up) or negative and falling (down)."""
    g = gap.to_numpy(dtype=float)
    out = np.zeros(len(g), dtype=int)
    for i in range(1, len(g)):
        ok = (g[i] > 0 and g[i] > g[i - 1]) if up else (g[i] < 0 and g[i] < g[i - 1])
        out[i] = out[i - 1] + 1 if ok else 0
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    e = {k: c.ewm(span=int(p[k]), adjust=False).mean() for k in ("f1", "f2", "s1", "s2")}
    ef, es = (e["f1"] + e["f2"]) / 2, (e["s1"] + e["s2"]) / 2
    xup, xdn = _streak(ef - es, True), _streak(ef - es, False)
    fup, fdn = _streak(e["f1"] - e["f2"], True), _streak(e["f1"] - e["f2"], False)
    sup, sdn = _streak(e["s1"] - e["s2"], True), _streak(e["s1"] - e["s2"], False)
    bcond = (xup >= 2) & (sup >= 2) & (fup >= 2)
    scond = (xdn >= 2) & (sdn >= 2) & (fdn >= 2)
    hv = np.maximum(o, c).to_numpy(dtype=float)
    lv = np.minimum(o, c).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    ts, tp, ttp = float(p["ts"]), float(p["tp"]), min(float(p["ttp"]), float(p["tp"]))
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    buy = sell = 0
    bs = 0
    in_long = False
    entry_c = 0.0
    last_high = np.nan
    in_close_prev = False
    for i in range(m):
        buy = (buy + 1 if buy > 0 else 1) if bcond[i] else 0
        sell = (sell + 1 if sell > 0 else 1) if scond[i] else 0
        bs_prev = bs
        if buy == 1 and bs <= 0:
            bs = 1
        elif sell == 1 and bs >= 0:
            bs = -1
        cond = bs != bs_prev and bs == 1
        if cond:
            entry_c, in_long = cv[i], True
        if not in_long:
            last_high = np.nan
        elif np.isnan(last_high) or hv[i] > last_high:
            last_high = hv[i]
        l_ts = not np.isnan(last_high) and lv[i] <= last_high * (1 - ts)
        l_tp = (not np.isnan(last_high) and last_high >= entry_c * (1 + tp) and lv[i] <= last_high * (1 - ttp))
        close_ = (l_tp or l_ts) and not cond
        in_close = True if close_ else (False if cond else in_close_prev)
        nxt = held
        if cond and not held and i + 1 < m:
            le[i], nxt = True, True
        if close_ and not in_close_prev and held:
            lx[i], nxt = True, False
        if close_ or not in_long:
            last_high = np.nan
        if close_ and not in_close_prev and bs == 1:
            bs = 0
        in_close_prev = in_close
        held = nxt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
