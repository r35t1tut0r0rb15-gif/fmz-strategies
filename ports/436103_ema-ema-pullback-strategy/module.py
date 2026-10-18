"""EMA pullback entries with a risk-sized bracket, 1-hour bars, from flat: a close back over the EMA 33 after a pullback that closed under the EMA 165, in an EMA 33 over
EMA 365 trend, goes long when the pullback depth (close to its low) exceeds 0.8 %, with the stop at that low and a target 2.06 times the risk; the mirror goes short.
Port of FMZ strategy #436103 "EMA黄金交叉回调策略EMA-Pullback-Strategy" (EMA pullback strategy).

FMZ source id: 436103

Source
    https://www.fmz.com/strategy/436103 (PineScript v4, FMZ last modified 2023-12-21 11:48:54).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 163-279), EMA 33 / 165 / 365; risk limits 0.8 % to 2 %; target : stop ratio 2.06
    long = crossover(close, ema33) and minClose(since the last crossunder) < ema165 and ema33 > ema365;  risk_long = (close - minLow(since the last crossunder)) / close;  flat and long and risk_long > 0.008 -> entry long, exit(stop = avg (1 - risk_long), limit = avg (1 + 2.06 risk_long))
    short mirrors with the high since the last crossover

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pullback extremes restart at each crossing and are updated by every bar since. The bracket is a
      fraction of the fill price with the risk from the signal bar: sl_stop = risk, tp_stop = ratio x
      risk (shifted one bar inside stops(), re-based on the fill). A signal whose risk is not over the lowest limit
      places no entry. The quantity capped by the highest risk limit (2 % of equity per trade) is
      sizing. Entries only from flat: "flat" follows the house bracket on bars. Opposite entries
      cannot occur. The start date is the author's window: dropped. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA structure and a risk-sized bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based, risk-capped quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436103_ema_pullback_risk_bracket"
FAMILY = "pullback"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ratio": [2.06, 3.0],
    "risk_low": [0.008, 0.015],
}
DEFAULT_PARAMS = {"ratio": 2.06, "risk_low": 0.008, "e1": 33, "e2": 165, "e3": 365}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e1 = c.ewm(span=int(p["e1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["e2"]), adjust=False).mean()
    e3 = c.ewm(span=int(p["e3"]), adjust=False).mean()
    xo = ((c > e1) & (c.shift(1) <= e1.shift(1))).to_numpy()
    xu = ((c < e1) & (c.shift(1) >= e1.shift(1))).to_numpy()
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    e2v, e1v, e3v = e2.to_numpy(), e1.to_numpy(), e3.to_numpy()
    m = len(cv)
    max_close = max_high = min_close = min_low = np.nan
    ratio, rlow = float(p["ratio"]), float(p["risk_low"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl = np.full(m, np.nan)
    pos, ei, s_ = 0, -1, np.nan
    for i in range(m):
        if xo[i]:
            max_close, max_high = cv[i], hv[i]
        if cv[i] > max_close:
            max_close = cv[i]
        if hv[i] > max_high:
            max_high = hv[i]
        if xu[i]:
            min_close, min_low = cv[i], lv[i]
        if cv[i] < min_close:
            min_close = cv[i]
        if lv[i] < min_low:
            min_low = lv[i]
        if pos != 0 and i >= ei:                          # the house bracket from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - s_) or hv[i] >= e0 * (1 + ratio * s_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + s_) or lv[i] <= e0 * (1 - ratio * s_)):
                pos = 0
        if pos == 0:
            long_c = xo[i] and min_close < e2v[i] and e1v[i] > e3v[i]
            short_c = xu[i] and max_close > e2v[i] and e1v[i] < e3v[i]
            if long_c:
                risk = (cv[i] - min_low) / cv[i]
                if risk > rlow:
                    le[i], pos, ei, s_ = True, 1, i + 1, risk
                    sl[i] = s_
            elif short_c:
                risk = (max_high - cv[i]) / cv[i]
                if risk > rlow:
                    se[i], pos, ei, s_ = True, -1, i + 1, risk
                    sl[i] = s_
    return le, se, sl, sl * ratio


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
