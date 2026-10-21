"""Fisher transform of a Hull MA with CCI and Hull slope filters, broker days: the Fisher line above its previous value, beyond -5 from below or above 0, with the CCI 14 and the Hull MA 14 (both of the open)
rising goes long; the mirror goes short; a falling Hull or Fisher closes a long, a rising one closes a short; reversing.
Port of FMZ strategy #438940 "优化自适应智能多因子Hull渔人策略Hull-Fisher-Adaptive-Intelligent-Multi-factor-Strategy" (Hull Fisher).

FMZ source id: 438940

Source
    https://www.fmz.com/strategy/438940 (PineScript v4, FMZ last modified 2024-01-16 15:10:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-221), Hull 14, signal 9, lines 5 / -5 on the open; both entry types on; CCI and HMA filters on; Fisher and Hull closes on; 100 % of equity, commission 0.25 %
    value := clip(0.66 ((hma - lowest(hma, 9)) / max(range, 0.001) - 0.5) + 0.67 value[1]);  value1 := 0.5 log((1 + value) / max(1 - value, 0.001)) + 0.5 value1[1];  value2 = value1[1]
    long = value1 > value2 and (value1 < -5 or value1 > 0) and cci > cci[1] and hma > hma[1];  short mirror (value1 > 5 or value1 < 0);  hma < hma[1] or value1 < value2 -> close BUY;  the mirror -> close SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * With CCI and HMA both on, only conditions 7 and 8 apply. The closes come before the entries and act
      on the position held at the bar close; an entry bar always closes the opposite side, then reverses.
      The Hull MA uses floor(n / 2) and round(sqrt(n)). strategy.entry reverses: REVERSAL INTENDED. The size
      and commission are sizing / costs. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Fisher transform of a Hull MA, CCI and slopes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_438940_hull_fisher_cci_filters"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 28],
    "length": [9, 18],
}
DEFAULT_PARAMS = {"period": 14, "length": 9, "line1": 5.0, "line5": -5.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n) + 0.5)))


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (src - ma) / (0.015 * dev)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    price = bars_df["open"]
    n = int(p["period"])
    hma = _hma(price, n)
    k = int(p["length"])
    hi, lo_ = hma.rolling(k).max(), hma.rolling(k).min()
    raw = ((hma - lo_) / np.maximum(hi - lo_, 0.001) - 0.5).to_numpy()
    m = len(raw)
    v = np.zeros(m)
    v1 = np.full(m, np.nan)
    pv = pv1 = 0.0
    for i in range(m):
        x = 0.66 * raw[i] + 0.67 * pv
        x = 0.999 if x > 0.99 else (-0.999 if x < -0.99 else x)
        v[i] = x
        y = 0.5 * np.log((1 + x) / max(1 - x, 0.001)) + 0.5 * pv1 if not np.isnan(x) else np.nan
        v1[i] = y
        pv = 0.0 if np.isnan(x) else x
        pv1 = 0.0 if np.isnan(y) else y
    s1 = pd.Series(v1, index=price.index)
    s2 = s1.shift(1)
    cci = _cci(price, n)
    hma2, cci2 = hma.shift(1), cci.shift(1)
    l1, l5 = float(p["line1"]), float(p["line5"])
    long_c = ((s1 > s2) & ((s1 < l5) | (s1 > 0)) & (cci > cci2) & (hma > hma2)).to_numpy()
    short_c = ((s1 < s2) & ((s1 > l1) | (s1 < 0)) & (cci < cci2) & (hma < hma2)).to_numpy()
    close_b = ((hma < hma2) | (s1 < s2)).to_numpy()
    close_s = ((hma > hma2) | (s1 > s2)).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif short_c[i] and pos != -1 and i + 1 < m:
            se[i], pos = True, -1
        elif pos == 1 and close_b[i]:
            lx[i], pos = True, 0
        elif pos == -1 and close_s[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
