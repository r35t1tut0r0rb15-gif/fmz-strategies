"""Twin OTT, 4-hour bars: a VAR (CMO-adaptive) moving average crossing above the upper OTT line of two bars
ago goes long, crossing below the lower OTT line of two bars ago goes short.
Port of FMZ strategy #428705 "双OTT趋势跟踪策略Twin-Optimized-Trend-Tracker-Strategy" (Twin Optimized Trend Tracker).

FMZ source id: 428705

Source
    https://www.fmz.com/strategy/428705 (PineScript v4, FMZ last modified 2023-10-08 15:10:31).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-290), OTT period 40, constant 1 %, twin coefficient 0.001, MA type VAR
    VAR := alpha x |CMO9| x src + (1 - alpha x |CMO9|) x VAR[1]   (alpha = 2 / (40 + 1))
    longStop / shortStop = VAR -/+ 1 % ratcheted; dir flips on VAR vs the previous stops; MT = the active stop
    OTT = VAR > MT ? MT x (200 + 1) / 200 : MT x (200 - 1) / 200; OTTup / OTTdn = OTT x (1 +/- 0.001)
    crossover(VAR, OTTup[2]) -> entry long; crossunder(VAR, OTTdn[2]) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default MA type (VAR) is ported; the other types are input options. VAR starts from
      0 (nz) and the CMO is 0 until 9 bars exist, as written.
    * The OTT lines are signals, not stops. The date-range inputs are not used by the orders.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percentages of the moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND361567 (3 members, best partner #433011, Jaccard 0.661); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428705_twin_ott_var"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [40, 20],
    "percent": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 40, "percent": 1.0, "coeff": 0.001, "cmo_length": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"]
    d = src.diff()
    ud = d.where(d > 0, 0.0).fillna(0.0)
    dd = (-d).where(d < 0, 0.0).fillna(0.0)
    n9 = int(p["cmo_length"])
    vud, vdd = ud.rolling(n9).sum(), dd.rolling(n9).sum()
    cmo = ((vud - vdd) / (vud + vdd)).replace([np.inf, -np.inf], np.nan).fillna(0.0).abs().to_numpy()
    s = src.to_numpy()
    a = 2.0 / (int(p["length"]) + 1)
    m = len(s)
    var = np.zeros(m)
    for i in range(m):
        prev = var[i - 1] if i >= 1 else 0.0
        var[i] = a * cmo[i] * s[i] + (1 - a * cmo[i]) * prev
    pct = float(p["percent"])
    ls_, ss_ = np.full(m, np.nan), np.full(m, np.nan)
    direc = np.ones(m, dtype=np.int8)
    ott = np.full(m, np.nan)
    for i in range(m):
        f = var[i] * pct * 0.01
        lraw, sraw = var[i] - f, var[i] + f
        lp = ls_[i - 1] if i >= 1 else lraw
        sp = ss_[i - 1] if i >= 1 else sraw
        ls_[i] = max(lraw, lp) if var[i] > lp else lraw
        ss_[i] = min(sraw, sp) if var[i] < sp else sraw
        dprev = direc[i - 1] if i >= 1 else 1
        if dprev == -1 and var[i] > sp:
            dcur = 1
        elif dprev == 1 and var[i] < lp:
            dcur = -1
        else:
            dcur = dprev
        direc[i] = dcur
        mt = ls_[i] if dcur == 1 else ss_[i]
        ott[i] = mt * (200 + pct) / 200 if var[i] > mt else mt * (200 - pct) / 200
    idx = bars_df.index
    v = pd.Series(var, index=idx)
    up2 = pd.Series(ott * (1 + p["coeff"]), index=idx).shift(2)
    dn2 = pd.Series(ott * (1 - p["coeff"]), index=idx).shift(2)
    long_e = ((v > up2) & (v.shift(1) <= up2.shift(1))).astype(bool)
    short_e = ((v < dn2) & (v.shift(1) >= dn2.shift(1))).astype(bool)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
