"""EMA-ribbon crossings with a WaveTrend "blood diamond" filter, 2-hour bars: EMA 11 crossing over EMA 34, or over EMA 15 without a blood diamond, goes long with a stop at the lowest low since the last short signal (else 2 % under the close) and a 2 R target; EMA 34 crossing over EMA 11, or a blood diamond, goes short with a stop at the highest high since the last long signal (else 2 % over) and a 3 R target; reversing.
Port of FMZ strategy #477580 "高级WaveTrend与EMA-Ribbon融合交易策略-Advanced-WaveTrend-and-EMA-Ribbon-Fusion-Trading-Strategy" (VuManChu Cipher A Strategy).

FMZ source id: 477580

Source
    https://www.fmz.com/strategy/477580 (PineScript v5, FMZ last modified 2025-01-06 15:21:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-221), WaveTrend 9 / 13 / 3 of hlc3; EMA ribbon 5 / 11 / 15 / 18 / 21 / 24 / 28 / 34; qty 1, capital 10000
    longEma = crossover(ema11, ema34);  shortEma = crossover(ema34, ema11);  redCross = crossunder(ema5, ema11);  blueTriangle = crossover(ema11, ema15);  bloodDiamond = cross(wt1, wt2) and wt2 - wt1 >= 0 and redCross
    long = longEma or (blueTriangle and not bloodDiamond) -> highest := high, stop := nz(lowestSinceShort, close x 0.98), target := close + 2 |close - stop|, entry + exit
    short = shortEma or bloodDiamond -> lowest := low, stop := nz(highestSinceLong, close x 1.02), target := close - 3 |stop - close|, entry + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop follows the trackers in the script's order (each bar first extends the highest high since
      the last long signal and the lowest low since the last short signal, then the long and short
      blocks reset them), and the opening signal's levels are sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). blueTriangle can repeat inside
      a long and re-sends the bracket, which is not followed (as #434428, mark trailing_stop_pending). On a
      bar with both signals the later short call wins (#437773), with its stop from the high just reset.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour:
      mark coarse_bar_stop. The fixed qty 1 and capital are sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, EMA-ribbon / WaveTrend signals with swing stops and R targets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 and capital 10000 stored, not ported.
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

NAME = "fmz_477580_ema_ribbon_wavetrend_swing_stop_r_target_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_rr": [2.0, 1.5],
    "short_rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"long_rr": 2.0, "short_rr": 3.0}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _run(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + c) / 3
    esa = _ema(src, 9)
    de = _ema((src - esa).abs(), 9)
    ci = (src - esa) / (0.015 * de)
    wt1 = _ema(ci, 13)
    wt2 = wt1.rolling(3).mean()
    d = wt1 - wt2
    wt_cross = ((d > 0) & (d.shift(1) <= 0)) | ((d < 0) & (d.shift(1) >= 0))
    e5, e11, e15, e34 = (_ema(c, n) for n in (5, 11, 15, 34))

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    red_cross = xo(e11, e5)
    blood = wt_cross & (wt2 - wt1 >= 0) & red_cross
    lc = (xo(e11, e34) | (xo(e11, e15) & ~blood)).to_numpy()
    sc = (xo(e34, e11) | blood).to_numpy()
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    krl, krs = float(p["long_rr"]), float(p["short_rr"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_s, tp_s, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    last_l = last_s = hsl = lss = np.nan
    for i in range(m):
        if not np.isnan(last_l):
            hsl = max(hv[i], 0.0 if np.isnan(hsl) else hsl)
        if not np.isnan(last_s):
            lss = min(lv[i], 0.0 if np.isnan(lss) else lss)
        if lc[i]:
            last_l, hsl = cv[i], hv[i]
            stop = cv[i] * 0.98 if np.isnan(lss) else lss
            le[i], sl_s[i], tp_s[i], side[i] = True, stop, cv[i] + abs(cv[i] - stop) * krl, 1
        if sc[i]:
            last_s, lss = cv[i], lv[i]
            stop = cv[i] * 1.02 if np.isnan(hsl) else hsl
            le[i] = False
            se[i], sl_s[i], tp_s[i], side[i] = True, stop, cv[i] - abs(stop - cv[i]) * krs, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, se, sl_s, tp_s, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl_s, tp_s, side = _run(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    sl1, tp1 = sl_s.shift(1), tp_s.shift(1)
    l_thr = (sl1 >= o) | (tp1 <= o)       # marketable at the fill
    s_thr = (sl1 <= o) | (tp1 >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl_s, tp_s, side = _run(bars_df, p)
    o = bars_df["open"]
    sl1, tp1, sd = sl_s.shift(1), tp_s.shift(1), side.shift(1)
    sl_f = (1 - sl1 / o).where(sd > 0, sl1 / o - 1)
    tp_f = (tp1 / o - 1).where(sd > 0, 1 - tp1 / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
