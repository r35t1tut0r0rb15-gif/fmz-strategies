"""WaveTrend 9 / 12 / 3 extremes or crossings with the last completed hour's close beyond the EMA 200 of highs (lows), 1-minute bars: while the wave is oversold (and has been for 2 bars, or crosses up) with the close over the EMA 12 in a bullish channel, go long with a stop under the extreme low (or the low EMA) and a 3 R target; the mirror goes short; reversing.
Port of FMZ strategy #490787 "Multi Timeframe Dynamic Momentum Wave Capture Strategy" (Enhanced Momentum Wave Catcher).

FMZ source id: 490787

Source
    https://www.fmz.com/strategy/490787 (PineScript v5, FMZ last modified 2025-04-16 14:53:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-290), EMA 12; EMA 200 of high / low; WaveTrend 9 / 12 / 3; levels -50 / 50; confirmation 1; RR 3; risk 100 USD sizing
    wt2 <= -50 -> oversold count += 1, extreme low := min(low, ...) else reset (na);  overbought mirror
    hourly close (security "60") > ema200(high) -> above;  < ema200(low) -> below (kept)
    above and (oversold count > 1 or crossover(wt1, wt2)) and close > ema12 and stop = min(extreme low, ema200low x 0.998) not na -> entry Long + exit(stop, limit = close + 3 (close - stop));  mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "60" request without lookahead is read as the last completed hour (as #440503), built from the
      module's own bars. The stop needs a current extreme (math.min with na is na), so a long needs the wave
      oversold on the signal bar. The counters, extremes and channel flags are followed in a loop. The
      bracket is set on the signal bar and sent as fractions of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256). Same-side signals repeat while held, each re-sending
      the bracket; the port keeps the opening levels, mark trailing_stop_pending (as #434428). An entry on
      the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The
      risk-sized quantity is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; extreme / EMA bracket as fractions of the fill.
    2 generic: PASS, WaveTrend extremes with an hourly channel filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity (100 USD) and capital stored, not ported.
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

NAME = "fmz_490787_wavetrend_extreme_hourly_ema200_channel_3r_reversal"
FAMILY = "wavetrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rrRatio": [3.0, 1.5],
    "overboughtLevel": [50, 60],
}
DEFAULT_PARAMS = {"rrRatio": 3.0, "overboughtLevel": 50, "fastEmaLength": 12, "slowEmaLength": 200,
                  "confirmationBars": 1}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    fe = ema(c, p["fastEmaLength"])
    eh, el = ema(h, p["slowEmaLength"]), ema(lo, p["slowEmaLength"])
    hour = c.index.floor("1h")
    hc = c.groupby(hour).last()
    h_close = pd.Series(hc.shift(1).reindex(hour).to_numpy(), index=c.index)   # last completed hour
    src = (h + lo + c) / 3
    esa = ema(src, 9)
    de = ema((src - esa).abs(), 9)
    ci = (src - esa) / (0.015 * de.where(de != 0))
    wt1 = ema(ci, 12)
    wt2 = wt1.rolling(3).mean()
    xu = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))).to_numpy()
    xd = ((wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))).to_numpy()
    ob = float(p["overboughtLevel"])
    w2, hv, lv, cv = wt2.to_numpy(), h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    hcv, ehv, elv, fev = h_close.to_numpy(), eh.to_numpy(), el.to_numpy(), fe.to_numpy()
    cb = int(p["confirmationBars"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lsl, ssl = np.full(m, np.nan), np.full(m, np.nan)
    osb = obb = 0
    ex_lo = ex_hi = np.nan
    above = below = False
    for i in range(m):
        if w2[i] <= -ob:
            osb += 1
            ex_lo = lv[i] if np.isnan(ex_lo) else min(lv[i], ex_lo)
        else:
            osb, ex_lo = 0, np.nan
        if w2[i] >= ob:
            obb += 1
            ex_hi = hv[i] if np.isnan(ex_hi) else max(hv[i], ex_hi)
        else:
            obb, ex_hi = 0, np.nan
        if hcv[i] > ehv[i]:
            above, below = True, False
        elif hcv[i] < elv[i]:
            above, below = False, True
        ls = np.nan if np.isnan(ex_lo) else min(ex_lo, elv[i] * 0.998)
        ss = np.nan if np.isnan(ex_hi) else max(ex_hi, ehv[i] * 1.002)
        if above and (osb > cb or xu[i]) and cv[i] > fev[i] and not np.isnan(ls):
            le[i], lsl[i] = True, ls
        if below and (obb > cb or xd[i]) and cv[i] < fev[i] and not np.isnan(ss):
            se[i], ssl[i] = True, ss
    rr = float(p["rrRatio"])
    ix = c.index
    lsl_s, ssl_s = pd.Series(lsl, index=ix), pd.Series(ssl, index=ix)
    lvl = {"l_sl": lsl_s, "l_tp": c + rr * (c - lsl_s), "s_sl": ssl_s, "s_tp": c - rr * (ssl_s - c)}
    le_s, se_s = pd.Series(le, index=ix), pd.Series(se, index=ix)
    return le_s & ~se_s, se_s, lvl


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
