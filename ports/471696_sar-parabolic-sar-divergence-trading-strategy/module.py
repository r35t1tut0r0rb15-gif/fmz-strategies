"""Price-versus-SAR disagreements five bars back, daily bars: a falling close with a rising parabolic SAR five bars ago goes long, a rising close with a falling SAR goes short; reversing.
Port of FMZ strategy #471696 "抛物线SAR指标背离交易策略-Parabolic-SAR-Divergence-Trading-Strategy" (SAR Divergence Strategy).

FMZ source id: 471696

Source
    https://www.fmz.com/strategy/471696 (PineScript v5, FMZ last modified 2024-11-12 15:12:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 126-162), ta.sar(14, 0.02, 0.2) (start 14 as written); lookback 5
    close[5] < close[6] and sar[5] > sar[6] -> entry Long;  close[5] > close[6] and sar[5] < sar[6] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar takes (start, increment, maximum), so the "length" 14 is the starting acceleration, as
      written (Pine's ta.sar as documented). The signals look only at bars 5 and 6 back. There is no
      exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SAR direction disagreements.
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

NAME = "fmz_471696_close_vs_sar_divergence_lag5_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_start": [14.0, 0.02],
    "lookback": [5, 1],
}
DEFAULT_PARAMS = {"sar_start": 14.0, "sar_inc": 0.02, "sar_max": 0.2, "lookback": 5}


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
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"])), index=c.index)
    k = int(p["lookback"])
    ck, ck1, sk, sk1 = c.shift(k), c.shift(k + 1), sar.shift(k), sar.shift(k + 1)
    le = (ck < ck1) & (sk > sk1)
    se = (ck > ck1) & (sk < sk1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
