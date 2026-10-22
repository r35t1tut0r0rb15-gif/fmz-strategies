"""Three Line Strike candles with a hand-built ADX 14 over 25, hourly bars: three red candles then a larger green engulfing one goes long, three green then a larger red goes short, each with a 1 ATR 14 stop and a 2 ATR target from the signal close; reversing.
Port of FMZ strategy #482921 "三线突破动量趋势跟踪策略结合ADX过滤器-Three-Line-Strike-Momentum-Trend-Following-Strategy-with-ADX-Filter" (3 Line Strike [TTF] - Strategy with ATR and ADX Filter).

FMZ source id: 482921

Source
    https://www.fmz.com/strategy/482921 (PineScript v5, FMZ last modified 2025-02-20 17:46:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-195), ATR 14; ADX 14 (hand-built from ta.change); threshold 25; TP 2 ATR; SL 1 ATR; pyramiding 0; 100 % of equity, capital 100000
    3 red candles [1..3] and green candle larger than the last -> 3LS Bull;  3 green [1..3] and larger red -> 3LS Bear;  each with adx > 25
    3LS Bull -> entry 3LS_Bull + exit(limit = close + 2 atr, stop = close - atr);  3LS Bear -> entry 3LS_Bear + exit(limit = close - 2 atr, stop = close + atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is kept as written: minusDM uses ta.change(low) (a rising low) in place of the fall of the
      low, so it is not Wilder's ADX. "Larger" compares the bodies' absolute sizes. The levels are fixed
      at the signal close and sent as fractions of the fill open (a level at or through it is marketable
      and closed one bar late, as #458256). A repeat signal while held re-sends the bracket; stops()
      keeps the first, so the repeat case is marked trailing_stop_pending (as #434428). An entry on the
      other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The show
      switches are on as defaulted. The 100 % of equity size and the capital are sizing. Near-duplicate
      of #483019 (DG482921), ported under rule 7. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, three-line-strike candles with an ADX filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG482921 (2 members, best partner #483019, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482921_three_line_strike_adx25_atr_1_2_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [25.0, 20.0],
    "tp_atr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"adx_threshold": 25.0, "tp_atr": 2.0, "sl_atr": 1.0, "atr_length": 14, "adx_length": 14}


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


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_length"]))
    n = int(p["adx_length"])
    ch, cl = h.diff(), lo.diff()
    pdm = ch.where((ch > cl) & (ch > 0), 0.0)
    mdm = cl.where((cl > ch) & (cl > 0), 0.0)          # as written: the change of the low, not its fall
    trs = _rma(tr, n)
    pdi, mdi = _rma(pdm, n) / trs * 100, _rma(mdm, n) / trs * 100
    adx = _rma((pdi - mdi).abs() / (pdi + mdi) * 100, n)
    col = np.sign(c - o)
    larger = (c - o).abs() > (c.shift(1) - o.shift(1)).abs()
    bull = (col.shift(1) < 0) & (col.shift(2) < 0) & (col.shift(3) < 0) & larger & (col > 0) & (col.shift(1) < 0)
    bear = (col.shift(1) > 0) & (col.shift(2) > 0) & (col.shift(3) > 0) & larger & (col < 0) & (col.shift(1) > 0)
    thr = float(p["adx_threshold"])
    se = bear & (adx > thr)
    le = bull & (adx > thr) & ~se
    a, b = atr * float(p["sl_atr"]), atr * float(p["tp_atr"])
    lvl = {"l_sl": c - a, "l_tp": c + b, "s_sl": c + a, "s_tp": c - b}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
