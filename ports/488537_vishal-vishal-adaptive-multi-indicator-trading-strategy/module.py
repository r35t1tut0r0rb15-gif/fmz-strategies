"""Kept MACD 13 / 27 / 9, Parabolic SAR 0.02 / 0.2 and SuperTrend 3 / 11 states, 2-day bars: all three bullish goes long, all three bearish goes short; a close under (over) the SAR closes; reversing.
Port of FMZ strategy #488537 "Vishal-自适应多指标交易策略-Vishal-Adaptive-Multi-Indicator-Trading-Strategy" (Vishal Strategy).

FMZ source id: 488537

Source
    https://www.fmz.com/strategy/488537 (PineScript v6, FMZ last modified 2025-03-28 17:17:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-200), MACD 13 / 27 / 9; SuperTrend 3 / 11; SAR 0.02 / 0.02 / 0.2; capital 100000, 100 % of equity
    flags: macd > signal -> true, < -> false;  close > sar -> true, < -> false;  direction < 0 -> true, > 0 -> false (kept when equal)
    all true -> entry Long;  all false -> entry Short;  long and close < sar -> close Long;  short and close > sar -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The three flags keep their value when their two series are equal, so a loop follows them, as
      written. The SAR exit count needs only one close beyond the SAR. A short entry also meets the long
      exit, so it reverses (REVERSAL INTENDED). ta.supertrend and ta.sar follow Pine's reference
      implementations. Bars are blocks of two broker days (17:00 America/New_York) counted from
      1970-01-01, stamped with their first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD / SAR / SuperTrend agreement with a SAR exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: strategy(): capital 100000, 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488537_macd_sar_supertrend_flags_sar_exit_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atrPeriod": [11, 20],
}
DEFAULT_PARAMS = {"factor": 3.0, "atrPeriod": 11, "fast_length": 13, "slow_length": 27, "signal_length": 9,
                  "sarStep": 0.02, "sarMax": 0.2, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


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

    macd = ema(c, p["fast_length"]) - ema(c, p["slow_length"])
    sig = ema(macd, p["signal_length"])
    _, d = _supertrend(bars_df, float(p["factor"]), int(p["atrPeriod"]))
    sar = _sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
               float(p["sarStep"]), float(p["sarStep"]), float(p["sarMax"]))
    mv, sv, dv, cv = macd.to_numpy(), sig.to_numpy(), d.to_numpy(), c.to_numpy(dtype=float)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    fm = fs = ft = False
    for i in range(m):
        if mv[i] > sv[i]:
            fm = True
        if mv[i] < sv[i]:
            fm = False
        if cv[i] > sar[i]:
            fs = True
        if cv[i] < sar[i]:
            fs = False
        if dv[i] < 0:
            ft = True
        if dv[i] > 0:
            ft = False
        le[i] = fm and fs and ft
        se[i] = not fm and not fs and not ft
    sar_s = pd.Series(sar, index=c.index)
    le_s, se_s = pd.Series(le, index=c.index), pd.Series(se, index=c.index)
    return le_s, (c < sar_s) & ~se_s, se_s, (c > sar_s) & ~le_s


def portfolio_kwargs(**params):
    return {}
