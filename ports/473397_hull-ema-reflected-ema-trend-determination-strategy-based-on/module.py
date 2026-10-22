"""Reversal swings of a reflected Hull line, daily bars: the line 2 x HMA 36 - HMA 44, smoothed by HMA 2, is followed with its running peak and trough; a drop of 0.04 % from the peak in an up phase goes short, a rise of 0.04 % from the trough in a down phase goes long; reversing.
Port of FMZ strategy #473397 "基于Hull移动平均线的反射型EMA趋势判定策略-Reflected-EMA-Trend-Determination-Strategy-Based-on-Hull-Moving-Averages" (Reflected EMA Difference (RED)).

FMZ source id: 473397

Source
    https://www.fmz.com/strategy/473397 (PineScript v5, FMZ last modified 2024-11-29 16:35:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-188), HMA 36 / 44; smoothing HMA 2; correction 0.04 %
    refl = hma36 + (hma36 > hma44 ? |d| : -|d|);  s = hma(refl, 2);  dir >= 0: peak := max(peak, s), s <= peak x (1 - r) -> dir := -1, trough := s, entry Venta;  dir < 0: trough := min(trough, s), s >= trough x (1 + r) -> dir := 1, peak := s, entry Compra

Interpretation choices (Pine rules in SURVEY_README.md)
    * The reflected value is 2 x HMA 36 - HMA 44 on either side. The peak / trough state is a loop,
      seeded with the first valid smoothed value. The HMA 8 line and its crossings only feed commented
      boxes. HMA as Pine's ta.hma: WMA(2 x WMA(n / 2) - WMA(n), floor(sqrt(n))). There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, peak / trough reversals of a reflected Hull line.
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

NAME = "fmz_473397_reflected_hull_peak_trough_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "correction_pct": [0.04, 1.0],
    "smooth": [2, 5],
}
DEFAULT_PARAMS = {"correction_pct": 0.04, "smooth": 2}


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
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    refl = 2 * _hma(c, 36) - _hma(c, 44)
    s = _hma(refl, int(p["smooth"])).to_numpy(dtype=float)
    r = float(p["correction_pct"]) * 0.01
    m = len(s)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    d, pk, tr = 0, np.nan, np.nan
    for i in range(m):
        if np.isnan(pk):
            pk = s[i]
        if np.isnan(tr):
            tr = s[i]
        if d >= 0:
            if s[i] > pk:
                pk = s[i]
            if s[i] <= pk - pk * r:
                d, tr, se[i] = -1, s[i], True
        else:
            if s[i] < tr:
                tr = s[i]
            if s[i] >= tr + tr * r:
                d, pk, le[i] = 1, s[i], True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
