"""Parabolic SAR (start 0.02, increment and maximum 0.2, as written) with Bollinger 20 / 2, broker days: a close over the SAR and under the upper band goes long, a close under the SAR and over the lower band goes short; the long closes under the SAR or at the upper band, the short over the SAR or at the lower band; reversing.
Port of FMZ strategy #488417 "Parabolic SAR and Bollinger Bands Trend Identification Quantitative Trading Strategy" (Parabolic SAR + Bollinger Bands Strategy).

FMZ source id: 488417

Source
    https://www.fmz.com/strategy/488417 (PineScript v5, FMZ last modified 2025-03-27 14:20:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-225), ta.sar(0.02, 0.2, 0.2); BB 20 / 2
    close > sar and close < upper -> entry Buy;  close < sar or close >= upper -> close Buy
    close < sar and close > lower -> entry Sell;  close > sar or close <= lower -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar is called with (sar_step, sar_max, sar_max), so the increment is 0.2, as written. The
      conditions are states; a short entry also meets the long exit, so it reverses (REVERSAL INTENDED).
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Parabolic SAR side within the Bollinger bands.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_488417_psar_side_inside_bb20_2_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_max": [0.2, 0.1],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"sar_max": 0.2, "bb_mult": 2.0, "sar_step": 0.02, "bb_length": 20}


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
    mx = float(p["sar_max"])
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sar_step"]), mx, mx), index=c.index)
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    le = (c > sar) & (c < upper)
    se = (c < sar) & (c > lower)
    lx = ((c < sar) | (c >= upper)) & ~se
    sx = ((c > sar) | (c <= lower)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
