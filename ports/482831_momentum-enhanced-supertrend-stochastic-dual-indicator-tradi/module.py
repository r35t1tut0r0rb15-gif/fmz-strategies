"""Stochastic crosses below 20 (above 80) on the side of a SuperTrend-style ATR band regime, always in, daily bars.
Port of FMZ strategy #482831 "动量增强型超级趋势-随机双指标交易策略-Momentum-Enhanced-SuperTrend-Stochastic-Dual-Indicator-Trading-Strategy" (SuperTrend + Stochastic Strategy).

FMZ source id: 482831

Source
    https://www.fmz.com/strategy/482831 (PineScript v5, FMZ last modified 2025-02-20 14:51:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 136-181), ATR 10 x 3, stochastic 14 / 3 / 3
    upperBasic = hl2 + 3 ATR, lowerBasic = hl2 - 3 ATR; upperBand = close[1] > upperBand[1] ? max(upperBasic,
    upperBand[1]) : upperBasic; lowerBand = close[1] < lowerBand[1] ? min(lowerBasic, lowerBand[1]) : lowerBasic
    isBullish = close > upperBand[1] ? true : close < lowerBand[1] ? false : isBullish[1]
    K = sma(stoch(high, low, close, 14), 3), D = sma(K, 3)
    isBullish and crossover(K, D) and K < 20 -> entry long; not isBullish and crossunder(K, D) and K > 80 -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch's arguments are (source, high, low): the source passes (high, low, close), so K is
      100 x (high - lowest(close, 14)) / (highest(low, 14) - lowest(close, 14)) as written (it can leave 0-100).
    * The bands are ported as written (they widen, not tighten, when the close is beyond them).
    * Entries reverse (REVERSAL INTENDED); no exits, so always in after the first signal. Signal module, no stops.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands and a stochastic.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
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

NAME = "fmz_482831_atr_band_regime_stoch_cross_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [3.0, 2.0],
    "k_len": [14, 21],
}
DEFAULT_PARAMS = {"atr_len": 10, "multiplier": 3.0, "k_len": 14, "d_len": 3, "smooth_k": 3}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _regime(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, int(p["atr_len"]))
    mid = (h + lo) / 2
    ub_basic = (mid + p["multiplier"] * atr).to_numpy()
    lb_basic = (mid - p["multiplier"] * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ub, lb = np.full(m, np.nan), np.full(m, np.nan)
    bull = np.zeros(m, dtype=bool)
    state = True                          # var bool isBullish = true
    for i in range(m):
        if i == 0 or np.isnan(ub[i - 1]):
            ub[i], lb[i] = ub_basic[i], lb_basic[i]
        else:
            ub[i] = max(ub_basic[i], ub[i - 1]) if cv[i - 1] > ub[i - 1] else ub_basic[i]
            lb[i] = min(lb_basic[i], lb[i - 1]) if cv[i - 1] < lb[i - 1] else lb_basic[i]
        if i > 0 and cv[i] > ub[i - 1]:
            state = True
        elif i > 0 and cv[i] < lb[i - 1]:
            state = False
        bull[i] = state
    return pd.Series(bull, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["k_len"])
    ll, hh = c.rolling(n).min(), lo.rolling(n).max()      # stoch(high, low, close): source high, "high" low, "low" close
    k = (100 * (h - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    bull = _regime(bars_df, p)
    up = (k > d) & (k.shift(1) <= d.shift(1))
    dn = (k < d) & (k.shift(1) >= d.shift(1))
    long_e = (bull & up & (k < 20)).astype(bool)
    short_e = (~bull & dn & (k > 80)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
