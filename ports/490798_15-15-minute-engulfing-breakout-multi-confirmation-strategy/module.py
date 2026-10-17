"""Engulfing zones that break two opposite engulfings, traded on the retest with a zone bracket, 15-minute bars: a
bullish engulfing whose high is above the lows of at least two of the last ten bearish engulfings becomes the buy
zone; a later bar trading back into it (low <= zone high, close > zone low) goes long with the stop at the zone low
and the target at the zone high; sell zones mirrored.
Port of FMZ strategy #490798 "15分钟图表吞没突破多重确认策略-15-Minute-Engulfing-Breakout-Multi-Confirmation-Strategy" (15Min Engulfing Break Strategy).

FMZ source id: 490798

Source
    https://www.fmz.com/strategy/490798 (PineScript v6, FMZ last modified 2025-04-16 15:33:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 221-306), 10 stored engulfings per side, 2 breaks, offset 30 pips of 0.0001
    bullHighs / bearLows = highs / lows of the last 10 bullish / bearish engulfings (newest first)
    bullish engulfing with high > at least 2 stored bear lows -> buy zone = its high / low (sell zone mirrored)
    long = buy zone set and low <= zone high and close > zone low -> entry long + exit(stop = zone low - offset,
    limit = zone high + offset); the zone is cleared;  short mirrored with the sell zone

Interpretation choices (Pine rules in SURVEY_README.md)
    * The engulfing tests as written (open below / above the previous close, close beyond the previous open).
    * The 30-pip offset is 0.003 in price units: on the author's BTC_USDT a negligible fraction of a tick range,
      dropped as inert (criterion 2).
    * The bracket levels are the zone's, placed on the signal bar: sl_stop = (close - zone low) / close, tp_stop =
      (zone high - close) / close for a long, shifted one bar inside stops() and re-based on the fill. When the signal
      bar's close is already beyond the target (possible: only the low must reach the zone), the source's limit fills
      at once on the fill bar: no entry is emitted for that signal (a zero-length trade); the zone is still cleared.
    * Both exits share the id "TP/SL"; issued only on entry bars, so each binds to the entry it follows. A new zone
      retest while already in the trade re-places the bracket (the entry itself is ignored): mark
      trailing_stop_pending; the port keeps the bracket of the entry.
    * Entries reverse (REVERSAL INTENDED); on a bar with both signals the short (written last) wins.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; zone bracket from the signal bar (re-placement marked).
    2 generic: PASS, candle and zone levels; the inert price-unit offset dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_490798_engulfing_zone_retest_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "memory": [10, 5],
    "breaks": [2, 3],
}
DEFAULT_PARAMS = {"memory": 10, "breaks": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    mem, need = int(p["memory"]), int(p["breaks"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    dsl, dtp = np.full(m, np.nan), np.full(m, np.nan)
    bull_highs, bear_lows = [], []
    bz_h = bz_l = sz_h = sz_l = np.nan
    for i in range(1, m):
        bull = c[i - 1] < o[i - 1] and c[i] > o[i] and o[i] < c[i - 1] and c[i] > o[i - 1]
        bear = c[i - 1] > o[i - 1] and c[i] < o[i] and o[i] > c[i - 1] and c[i] < o[i - 1]
        if bull:
            bull_highs.insert(0, h[i])
            del bull_highs[mem:]
        if bear:
            bear_lows.insert(0, lo[i])
            del bear_lows[mem:]
        if bull and len(bear_lows) >= 2 and sum(h[i] > x for x in bear_lows) >= need:
            bz_h, bz_l = h[i], lo[i]
        if bear and len(bull_highs) >= 2 and sum(lo[i] < x for x in bull_highs) >= need:
            sz_h, sz_l = h[i], lo[i]
        if not np.isnan(bz_h) and lo[i] <= bz_h and c[i] > bz_l:
            s_, t_ = (c[i] - bz_l) / c[i], (bz_h - c[i]) / c[i]
            if s_ > 0 and t_ > 0:
                le[i], dsl[i], dtp[i] = True, s_, t_
            bz_h = bz_l = np.nan
        if not np.isnan(sz_l) and h[i] >= sz_l and c[i] < sz_h:
            s_, t_ = (sz_h - c[i]) / c[i], (c[i] - sz_l) / c[i]
            if s_ > 0 and t_ > 0:
                le[i], se[i], dsl[i], dtp[i] = False, True, s_, t_
            sz_h = sz_l = np.nan
    return le, se, dsl, dtp


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dsl, dtp = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(dsl, index=idx).shift(1), "tp_stop": pd.Series(dtp, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
