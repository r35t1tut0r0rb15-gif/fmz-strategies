"""HPotter's Commodity Selection Index state, 1-hour bars: CSI = K x ATR 14 x ADXR 14; below its 14-bar SMA the state is
long, above it short; always in the state's direction.
Port of FMZ strategy #433579 "Commodity Momentum Index Strategy" (Commodity Selection Index Backtest).

FMZ source id: 433579

Source
    https://www.fmz.com/strategy/433579 (PineScript v3, FMZ last modified 2023-11-28 16:27:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 165-195), point value 50, margin 3000, commission 10, length 14, reverse false
    K = 100 x (50 / sqrt(3000) / 160);  ADXR = (ADX + ADX[14]) / 2;  CSI = K x atr(14) x ADXR;  pos = CSI < sma(CSI, 14) ? 1 : CSI > sma ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * K only scales the line; the CSI is compared with its own average, so the rule is scale-free. ADX
      as the source's fADX (rma, fixnan). strategy.entry reverses: REVERSAL INTENDED. reverse is
      false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR x ADXR line against its own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point value / margin / commission constants only scale the line.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433579_csi_vs_average"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "point_value": 50.0, "margin": 3000.0, "commission": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v):
    out = v.copy()
    last = np.nan
    for i in range(len(out)):
        if np.isnan(out[i]):
            out[i] = last
        else:
            last = out[i]
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    trur = tr.ewm(alpha=1 / n, adjust=False).mean()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).ewm(alpha=1 / n, adjust=False).mean()
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).ewm(alpha=1 / n, adjust=False).mean()
    with np.errstate(invalid="ignore", divide="ignore"):
        plus = _fixnan((100 * pdm / trur).replace([np.inf, -np.inf], np.nan).to_numpy())
        minus = _fixnan((100 * mdm / trur).replace([np.inf, -np.inf], np.nan).to_numpy())
    s = plus + minus
    adx = 100 * pd.Series(np.abs(plus - minus) / np.where(s == 0, 1.0, s), index=c.index).ewm(alpha=1 / n,
                                                                                          adjust=False).mean()
    adxr = (adx + adx.shift(n)) * 0.5
    k = 100 * (float(p["point_value"]) / np.sqrt(float(p["margin"])) / (150 + float(p["commission"])))
    csi = (k * trur * adxr).to_numpy()
    ma = pd.Series(csi, index=c.index).rolling(n).mean().to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if csi[i] < ma[i]:
            pos = 1
        elif csi[i] > ma[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
