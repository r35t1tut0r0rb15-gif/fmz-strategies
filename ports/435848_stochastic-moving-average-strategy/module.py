"""Stochastic cross in the EMA 21 / 50 retrace zone, 1-hour bars, from flat: %K crossing over %D under 20 with the EMA 21 over the EMA 50 and
the close between them goes long with a 1 ATR stop and a 1 : 1 target; the mirror above 80 goes short.
Port of FMZ strategy #435848 "Stochastic Moving Average Strategy" (Stochastic Moving Average).

FMZ source id: 435848

Source
    https://www.fmz.com/strategy/435848 (PineScript v5, FMZ last modified 2023-12-19 11:41:40).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 227-301), stoch 14 / 3, levels 80 / 20, no look-back; EMA 21 / 50; ATR 14 x 1; risk : reward 1
    K = stoch(close, high, low, 14);  D = sma(K, 3);  validLong = crossover(K, D) and K < 20 and ema21 > ema50 and close < ema21 and close >= ema50 and flat;  validShort = crossover(D, K) and K > 80 and ema21 < ema50 and close > ema21 and close <= ema50 and flat
    stop = close -+ atr 1;  target = close +- (stop distance) rr;  entry long / short;  exit(limit = target, stop = stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal bar; the port expresses them as fractions of the signal
      close (sl_stop = ATR x mult / close, tp_stop = rr x sl_stop) shifted one bar inside stops()
      (re-based on the fill). Entries only from flat: "flat" follows the house bracket on bars.
      Opposite entries cannot occur. The reference-market filter is off by default (a second symbol:
      not ported). The lookback and the risk sizing options are off. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, stochastic cross, an EMA zone and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash order size and risk-sizing inputs stored.
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

NAME = "fmz_435848_stoch_cross_ema_retrace_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.0, 2.0],
    "rr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"atr_mult": 1.0, "rr": 1.0, "atr_len": 14, "k_len": 14, "d_len": 3, "ob": 80, "os": 20,
                  "ema1": 21, "ema2": 50}


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
    n = int(p["k_len"])
    with np.errstate(invalid="ignore", divide="ignore"):
        k = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    d = k.rolling(int(p["d_len"])).mean()
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    dist = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"])).to_numpy()
    lc = ((k > d) & (k.shift(1) <= d.shift(1)) & (k < float(p["os"])) & (e1 > e2) & (c < e1) & (c >= e2)).to_numpy()
    sc = ((d > k) & (d.shift(1) <= k.shift(1)) & (k > float(p["ob"])) & (e1 < e2) & (c > e1) & (c <= e2)).to_numpy()
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    rr = float(p["rr"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl = np.full(m, np.nan)
    pos, ei, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= ei:                          # the house bracket from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - s_) or hv[i] >= e0 * (1 + rr * s_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + s_) or lv[i] <= e0 * (1 - rr * s_)):
                pos = 0
        if pos == 0 and not np.isnan(dist[i]) and cv[i] > 0:
            if lc[i]:
                le[i], pos, ei, s_ = True, 1, i + 1, dist[i] / cv[i]
                sl[i] = s_
            elif sc[i]:
                se[i], pos, ei, s_ = True, -1, i + 1, dist[i] / cv[i]
                sl[i] = s_
    return le, se, sl, sl * rr


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
