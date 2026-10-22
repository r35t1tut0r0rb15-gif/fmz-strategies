"""Weekly EMA 20 regime with a 7-bar low ratchet, broker days, long only from flat: the previous close over the last completed week's EMA 20 plus 0.25 ATR 5 (without a 1.5 ATR 7-bar range) goes long; a close under the ratchet (highest 7-bar low less 1 ATR) or under the weekly EMA closes.
Port of FMZ strategy #482904 "基于多重级别EMA与RSI动态势能强度的比特币跨周期趋势交易策略-Multi-Timeframe-Bitcoin-Trading-Strategy-Based-on-EMA-and-RSI-Dynamic-Momentum-Strength" (Bitcoin Regime Filter Strategy).

FMZ source id: 482904

Source
    https://www.fmz.com/strategy/482904 (PineScript v6, FMZ last modified 2025-02-27 17:24:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-184), weekly EMA 20 via f_sec (security ... [1]); market close via f_sec("D"); ATR 5; RSI 7 filter off; 100 % of equity, capital 10000, commission 0.1 %
    htfEma = security("W", ema(close, 20))[1];  marketPrice = security("D", close)[1];  regime = marketPrice > htfEma + 0.25 atr5;  caution = regime and highest(high, 7) - low > 1.5 atr5
    regime and flat and not caution -> entry Buy, trailStop := na;  long -> trailStop := max(trailStop, highest(low, 7) - (caution[1] ? 0.2 atr5 : atr5))
    close < trailStop or close < htfEma -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * f_sec reads the security without lookahead and then takes [1] on historical bars. For "W" that is
      the weekly EMA 20 of the last broker week (Monday label) completed before the bar's own week, built
      from the module's daily bars (as the C143-C147 weekly reading); for "D" on the daily chart it is
      the previous close. The RSI momentum filter is off by default (useRSI false), so it is not ported.
    * The ratchet is checked on bar closes and sent as a close (an exit signal, no stop module; an
      author's trail checked on closes, C1). The flat gate and the ratchet are followed in a loop. Long
      only. The 100 % of equity size and the capital are sizing; the commission is a cost (the house cost
      model applies). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based ratchet exit.
    2 generic: PASS, weekly EMA regime with an ATR ratchet.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); broker weeks labelled by their Monday.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482904_weekly_ema20_regime_atr5_low7_ratchet_close_long"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 10],
    "regime_atr": [0.25, 0.5],
}
DEFAULT_PARAMS = {"ema_len": 20, "regime_atr": 0.25, "atr_length": 5, "ratchet_bars": 7, "caution_atr": 1.5}


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
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _weekly_prev_ema(bars_df, n):
    """EMA n of broker-week closes (weeks labelled by their Monday), read for each day as the value
    of the last week completed before the day's own week."""
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    wk = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    wclose = pd.Series(c.to_numpy(), index=wk).groupby(level=0).last()
    wema = wclose.ewm(span=int(n), adjust=False).mean()
    prev = wema.shift(1)                     # the week before each week
    return pd.Series(prev.reindex(wk).to_numpy(), index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    htf = _weekly_prev_ema(bars_df, int(p["ema_len"]))
    atr = _atr(bars_df, int(p["atr_length"]))
    regime = c.shift(1) > htf + atr * float(p["regime_atr"])
    k = int(p["ratchet_bars"])
    caution = regime & ((h.rolling(k).max() - lo) > atr * float(p["caution_atr"]))
    temp = lo.rolling(k).max() - atr.where(~caution.shift(1, fill_value=False), atr * 0.2)
    rg, cu, tv = regime.to_numpy(), caution.to_numpy(), temp.to_numpy(dtype=float)
    cv, hv = c.to_numpy(dtype=float), htf.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = pend_in = pend_out = False
    trail = np.nan
    for i in range(m):
        if pend_in:
            pos, pend_in = True, False
        if pend_out:
            pos, pend_out = False, False
        if rg[i] and not pos and not pend_in and not cu[i]:
            le[i], pend_in, trail = True, True, np.nan
        if pos and (np.isnan(trail) or tv[i] > trail):
            trail = tv[i]
        if pos and (cv[i] < trail or cv[i] < hv[i]):
            lx[i], pend_out = True, True
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
