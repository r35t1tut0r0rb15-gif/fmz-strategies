"""MACD 12 / 26 / 9 side with the close against the Parabolic SAR 0.02 / 0.02 / 0.2, broker days: MACD over its signal with the close over the SAR goes long, both under goes short; reversing.
Port of FMZ strategy #482806 "动量趋势跟踪型双指标MACD与抛物线SAR结合策略-Momentum-Trend-Following-Dual-Indicator-MACD-and-Parabolic-SAR-Combination-Strategy" (MACD + Parabolic SAR Strategy).

FMZ source id: 482806

Source
    https://www.fmz.com/strategy/482806 (PineScript v5, FMZ last modified 2025-02-27 17:45:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-163), MACD 12 / 26 / 9; SAR 0.02 / 0.02 / 0.2
    macd > signal and close > sar -> entry Long;  macd < signal and close < sar -> entry Short
    position long and short condition -> close Long;  position short and long condition -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states: each holds bar after bar, and a repeat entry on the side already held
      adds nothing (default pyramiding). The closes on the opposite condition coincide with the opposite
      entry, so each is a reversal: REVERSAL INTENDED. ta.sar as Pine documents it (the house _sar
      helper, as #458200). No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD side with the SAR side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482806_macd12_26_9_side_sar_side_state_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [12, 8],
    "sar_max": [0.2, 0.1],
}
DEFAULT_PARAMS = {"fast_len": 12, "sar_max": 0.2, "slow_len": 26, "signal_len": 9, "sar_start": 0.02,
                  "sar_increment": 0.02}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["fast_len"]) - ema(c, p["slow_len"])
    sig = ema(macd, p["signal_len"])
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sar_start"]), float(p["sar_increment"]), float(p["sar_max"])), index=c.index)
    le = (macd > sig) & (c > sar)
    se = (macd < sig) & (c < sar)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
