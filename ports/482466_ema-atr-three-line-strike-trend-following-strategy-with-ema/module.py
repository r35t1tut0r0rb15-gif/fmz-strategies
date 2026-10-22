"""Three-line-strike candles with an EMA 200 side filter, 2-hour bars: three red bars then a larger green engulfing bar above the EMA goes long, the mirror under the EMA goes short, each with a target 2 ATR and a stop 1 ATR from the signal close; reversing.
Port of FMZ strategy #482466 "三线突破趋势跟踪策略结合EMA动态过滤和ATR风险管理系统-Three-Line-Strike-Trend-Following-Strategy-with-EMA-Dynamic-Filter-and-ATR-Risk-Management-System" (3 Line Strike [TTF] - Strategy with ATR and EMA Filter).

FMZ source id: 482466

Source
    https://www.fmz.com/strategy/482466 (PineScript v5, FMZ last modified 2025-02-18 15:30:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-178), ATR 14; EMA 200; TP 2 ATR, SL 1 ATR; 100 % of equity; capital 100000; pyramiding 0
    bars 1-3 red and bar 0 green with |body| > |body[1]| and close > ema200 -> entry Long + exit(limit = close + 2 atr, stop = close - atr);  mirror (bars 1-3 green, bar 0 red, close < ema200) -> entry Short + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * A candle's colour is close against open (a doji is neither). The levels are fixed at the signal close
      and sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256). A repeat signal while the side is held re-sends the bracket from the new close;
      stops() keeps the first, so the repeat case is marked trailing_stop_pending (as #434428). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. The 100 % of equity size and capital are sizing. FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, three-line-strike candles with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482466_three_line_strike_ema200_atr_2_1_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_length": [200, 100],
    "tp_atr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"ema_length": 200, "tp_atr": 2.0, "sl_atr": 1.0, "atr_length": 14}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    body = c - o
    green, red = body > 0, body < 0
    bigger = body.abs() > body.shift(1).abs()
    g1, g2, g3 = green.shift(1, fill_value=False), green.shift(2, fill_value=False), green.shift(3, fill_value=False)
    r1, r2, r3 = red.shift(1, fill_value=False), red.shift(2, fill_value=False), red.shift(3, fill_value=False)
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    le = r1 & r2 & r3 & green & bigger & (c > ema)
    se = g1 & g2 & g3 & red & bigger & (c < ema)
    a = _atr(bars_df, int(p["atr_length"]))
    tp, sl = a * float(p["tp_atr"]), a * float(p["sl_atr"])
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


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
