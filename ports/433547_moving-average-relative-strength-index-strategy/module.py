"""RSI of the opens against its average, 10-minute bars: the RSI 8 of the open (centred on 0) has an SMA 34; when that
average falls to zero or below the strategy goes long, when it rises above zero it goes short; always in.
Port of FMZ strategy #433547 "Moving Average Relative Strength Index Strategy" (RSI versus SMA).

FMZ source id: 433547

Source
    https://www.fmz.com/strategy/433547 (PineScript v2, FMZ last modified 2023-11-28 14:07:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 198-264), RSI source open, length 8; MA 34; invert false; initial stop off; trailing stop on with 120 points and no offset
    rsi = RSI(open, 8) - 50 (rma);  rsiMa = sma(rsi, 34);  dir = 0 >= rsiMa
    not dir[1] and dir -> entry long (and close short);  dir[1] and not dir -> entry short (and close long)
    useTS and not useTSO -> exit(trail_points = 120) (no trail_offset)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default "invert" off the long side follows the average at or below zero, as written.
      The RSI uses the bar's own open (shunt 0), known at the bar's start.
    * strategy.exit with trail_points and no trail_offset only sets an activation level and places no
      trailing stop (dropped, as #433452). The initial stop is off. switchDelay is defined but unused.
    * The exit and entry of each flip happen on one bar: REVERSAL INTENDED. FREQ = "10min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an RSI average sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 10 % of equity stored.
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

NAME = "fmz_433547_rsi_open_sma_sign"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [8, 14],
    "ma_len": [34, 55],
}
DEFAULT_PARAMS = {"rsi_len": 8, "ma_len": 34}


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
    o = bars_df["open"]
    ch = o.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna()) - 50
    ma = r.rolling(int(p["ma_len"])).mean()
    d = (ma <= 0).to_numpy()
    valid = ma.notna().to_numpy()
    d1 = np.concatenate(([False], d[:-1]))
    v1 = np.concatenate(([False], valid[:-1]))
    le = d & ~d1 & valid & v1
    se = ~d & d1 & valid & v1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
