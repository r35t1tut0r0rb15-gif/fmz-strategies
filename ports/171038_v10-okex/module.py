"""Bull/bear regime from a 30-minute channel breaking the prior days' range; long in bull,
short in bear, hold otherwise ("牛熊小卖部" V1.0).
Port of FMZ strategy #171038 "牛熊小卖部策略V10_OKex合约" (bull-bear shop strategy V1.0, OKEx futures).

Source
    https://www.fmz.com/strategy/171038 (JavaScript, author "区班量化", FMZ last modified
    2019-10-24 13:44:56). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 187-246, 99-185)
    dhigh/dlow = TA.Highest/Lowest(daily records, dnum=5)   (current bar excluded, per the author)
    mhigh/mlow = TA.Highest/Lowest(30-min records, mnum=20)
    if mhigh>dhigh && mlow<dlow:  (mhigh+mlow) < (dhigh+dlow)*0.97 -> bear
                                  (mhigh+mlow) > (dhigh+dlow)*1.03 -> bull;  else neutral
    elif mhigh>dhigh -> bull;  elif mlow<dlow -> bear;  else neutral
    bull: cancel short orders, close all shorts, buy (adds up to half the account)
    bear: cancel long orders, close all longs, sell short (adds up to half)
    neutral: monkeyOper(), whose body is commented out -> nothing

Interpretation choices
    * Bars: the code requests PERIOD_M30 and PERIOD_D1, so FREQ = "30min" and the daily range is
      built inside simulate() from the 30-min bars grouped into broker days (17:00 New York).
    * Per the author's comments, both channels exclude the forming bar. On completed 30-min bar t
      the port uses bars t-mnum+1..t (all completed) and the dnum broker days before t's day.
    * Criterion 2: the +/-3 % test on the channel centres becomes `center_atr` x the daily
      Wilder ATR(14) of the last completed day: bear when mid_m < mid_d - k*ATR_d, bull when
      mid_m > mid_d + k*ATR_d (mid = (high+low)/2).
    * bull closes shorts and opens long in the same loop: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies). Neutral holds. The adds, the
      half-account cap and the alternating 20/21 status that re-buys every other loop are sizing
      (original_sizing.txt). No exit other than the opposite regime.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_171038_m30_vs_daily_range_regime"
FAMILY = "multi_timeframe_breakout_regime"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # code requests PERIOD_M30 (and PERIOD_D1, built from these bars)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mnum": [10, 20, 40],
    "dnum": [3, 5, 10],
    "center_atr": [0.5, 1.0, 1.5],
}
DEFAULT_PARAMS = {"mnum": 20, "dnum": 5, "center_atr": 1.0, "atr_length": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    day = broker_day(bars_df.index)
    daily = bars_df.groupby(day).agg({"high": "max", "low": "min", "close": "last"})
    prev_close = daily["close"].shift(1)
    tr = pd.concat([daily["high"] - daily["low"], (daily["high"] - prev_close).abs(),
                    (daily["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    dnum = int(p["dnum"])
    per_day = pd.DataFrame({
        "dhigh": daily["high"].rolling(dnum).max().shift(1),   # completed days before today
        "dlow": daily["low"].rolling(dnum).min().shift(1),
        "datr": _rma(tr, int(p["atr_length"])).shift(1),
    })
    on_bar = per_day.reindex(day)
    dhigh, dlow, datr = (on_bar[k].to_numpy() for k in ("dhigh", "dlow", "datr"))
    mnum = int(p["mnum"])
    mhigh = bars_df["high"].rolling(mnum).max().to_numpy()
    mlow = bars_df["low"].rolling(mnum).min().to_numpy()
    mid_m, mid_d = (mhigh + mlow) / 2, (dhigh + dlow) / 2
    band = p["center_atr"] * datr

    both = (mhigh > dhigh) & (mlow < dlow)
    bear_both = both & (mid_m < mid_d - band)
    bull_both = both & (mid_m > mid_d + band)
    bull = bull_both | (~both & (mhigh > dhigh))
    bear = bear_both | (~both & ~(mhigh > dhigh) & (mlow < dlow))

    m = len(bars_df)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if bull[i] and pos != 1:
            le[i], pos = True, 1
        elif bear[i] and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
