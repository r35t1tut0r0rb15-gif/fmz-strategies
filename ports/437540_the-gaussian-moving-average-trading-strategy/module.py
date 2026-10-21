"""Z-score of a Heikin-Ashi EMA against its own percentiles, 5-minute bars: the score crossing over the 10th percentile of its smoothed line, or the smoothed line crossing over its median, goes long; the smoothed line
crossing under its 90th or 10th percentile or its 100-bar high goes short; a crossing over the 100-bar high adds a second long id; reversing.
Port of FMZ strategy #437540 "The Gaussian Moving Average Trading Strategy" (TZS).

FMZ source id: 437540

Source
    https://www.fmz.com/strategy/437540 (PineScript v5, FMZ last modified 2024-01-03 16:06:45).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 149-209), score = z-score(ema(haClose, 10), 25), emaScore = ema(score, 20); percentiles over 50 bars; highest / lowest over 100; start 2023-06-01
    longCon = crossover(score, p10) or crossover(emaScore, p50);  addOn = crossover(score, highest(emaScore, 100));  shortCon = crossunder(emaScore, p90) or crossunder(emaScore, p10) or crossunder(emaScore, highest)
    longCon -> entry Long (and close Long if shortCon);  addOn -> entry LongNR2 (and close LongNR2 if shortCon);  shortCon -> entry Short (and close Short if longCon)

Interpretation choices (Pine rules in SURVEY_README.md)
    * haClose is ohlc4. The percentiles use linear interpolation over the last 50 values of emaScore
      (current included); stdev is the population deviation. With pyramiding 0 the second long id can only
      open a long from flat or reverse a short; each close acts only on its own id open at the bar's
      close. Orders follow the script's call order. The start date (2023-06-01) is a backtest window:
      dropped. REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, z-score against its own percentiles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437540_ha_zscore_percentile_cross"
FAMILY = "mean_reversion"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "z_len": [25, 50],
    "pct_len": [50, 100],
}
DEFAULT_PARAMS = {"z_len": 25, "pct_len": 50, "ema_src": 10, "ema_score": 20, "hl_len": 100}


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xunder(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hac = (o + h + lo + c) / 4
    x = hac.ewm(span=int(p["ema_src"]), adjust=False).mean()
    n = int(p["z_len"])
    with np.errstate(divide="ignore", invalid="ignore"):
        score = (x - x.rolling(n).mean()) / x.rolling(n).std(ddof=0)
    es = score.ewm(span=int(p["ema_score"]), adjust=False).mean()
    k = int(p["pct_len"])
    p10 = es.rolling(k).quantile(0.10, interpolation="linear")
    p50 = es.rolling(k).quantile(0.50, interpolation="linear")
    p90 = es.rolling(k).quantile(0.90, interpolation="linear")
    hi = es.rolling(int(p["hl_len"])).max()
    lcon = (_xover(score, p10) | _xover(es, p50)).to_numpy()
    add = _xover(score, hi).to_numpy()
    scon = (_xunder(es, p90) | _xunder(es, p10) | _xunder(es, hi)).to_numpy()
    seq = [("entry", "Long", 1, lcon), ("close", "Long", 1, lcon & scon),
           ("entry", "LongNR2", 1, add), ("close", "LongNR2", 1, add & scon),
           ("entry", "Short", -1, scon), ("close", "Short", -1, scon & lcon)]
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    side, oid = 0, None
    for t in range(m):
        calc_id = oid
        s, oo = side, oid
        for kind, eid, d, cond in seq:
            if not cond[t]:
                continue
            if kind == "entry":
                if s != d:
                    s, oo = d, eid
            elif calc_id == eid and oo == eid:
                s, oo = 0, None
        if s == 1 and side != 1:
            le[t] = True
        elif s == -1 and side != -1:
            se[t] = True
        elif s == 0 and side == 1:
            lx[t] = True
        elif s == 0 and side == -1:
            sx[t] = True
        side, oid = s, oo
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
