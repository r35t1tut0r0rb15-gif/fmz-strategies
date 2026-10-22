"""RSI / stochastic-RSI regimes with a weekly RSI filter, broker days, long only: a strong stretch (stochastic RSI held over 50 or RSI over 60 for 8 bars, with the weekly-close RSI over 45) confirmed by an RSI
turn goes long; a weak stretch (stochastic RSI under 5 or RSI under 30) confirmed by an RSI turn closes.
Port of FMZ strategy #442014 "Multi Timeframe RSI SRSI Trading Strategy" (RSI and Stochatic Strategy).

FMZ source id: 442014

Source
    https://www.fmz.com/strategy/442014 (PineScript v5, FMZ last modified 2024-02-18 16:13:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-238), RSI 14, stochastic 14, K 3, D 3; SRSI 5 / 50; RSI 30 / 60; diff 5; HTF RSI 45; trigger 8; HTF "W" on ticker BTC_USDT:swap; dates 2019-2030
    sell_stoch = lowest(K, 8) < 5 or highest(rsi, 8) < 30;  buy_stoch = (lowest(K, 8) > 50 or lowest(rsi, 8) > 60) and rsi(security(ticker, "W", close), 14) > 45
    ll = barssince(not sell_stoch) + 1;  sell_validation = (highest(rsi, ll) > rsi[ll] + 5 and rsi < rsi[ll]) or rsi < rsi[ll] - 5
    llb = barssince(not buy_stoch) + 1;  buy_validation = (lowest(rsi, llb) < rsi[llb] - 5 and rsi > rsi[llb]) or (rsi > 60 and rsi - rsi[8] > 0);  buy_stoch and buy_validation -> entry buy;  sell_stoch and sell_validation -> close buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ticker input defaults to the backtest's own pair (BTC_USDT:swap), read as the current
      instrument, as its label offers ("leave empty for current"). A version-5 request.security("W")
      without lookahead is read as the last completed higher bar: the previous broker week's close (Monday
      to Friday by broker-day label), built from the module's own bars; the RSI 14 then runs on that daily
      series, as written. The variable look-backs are ported as written. A close acts only on the held
      position. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, RSI / stochastic-RSI regimes and turns.
    3 crypto-exchange-only: no (exchange pair in the header and as the ticker input (read as the current instrument)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442014_rsi_srsi_regime_turn_weekly_filter_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tr_dur": [8, 5],
    "diff": [5, 10],
}
DEFAULT_PARAMS = {"tr_dur": 8, "diff": 5, "rsi_length": 14, "stoch_length": 14, "k_smooth": 3, "st_low": 5,
                  "st_hi": 50, "rsi_low": 30, "rsi_hi": 60, "rsi_ht_hi": 45}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _since_not(flag):
    """barssince(not flag) + 1 (NaN before the first false)."""
    out = np.full(len(flag), np.nan)
    k = -1
    for i, f in enumerate(flag):
        if not f:
            k = 0
        elif k >= 0:
            k += 1
        if k >= 0:
            out[i] = k + 1
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["stoch_length"])
    rl, rh = r.rolling(n).min(), r.rolling(n).max()
    srsi = 100 * (r - rl) / (rh - rl).where(rh > rl)
    k = srsi.rolling(int(p["k_smooth"])).mean()
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk = c.groupby(week).last().shift(1)                  # last completed week
    cl2 = pd.Series(wk.reindex(week).to_numpy(), index=c.index)
    r2 = _rsi(cl2, 14)
    td = int(p["tr_dur"])
    sell_st = ((k.rolling(td).min() < float(p["st_low"])) | (r.rolling(td).max() < float(p["rsi_low"]))).to_numpy()
    buy_st = (((k.rolling(td).min() > float(p["st_hi"])) | (r.rolling(td).min() > float(p["rsi_hi"])))
              & (r2 > float(p["rsi_ht_hi"]))).to_numpy()
    rv = r.to_numpy(dtype=float)
    dff, rhi = float(p["diff"]), float(p["rsi_hi"])
    ll, llb = _since_not(sell_st), _since_not(buy_st)
    m = len(rv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0
    for i in range(m):
        sv = bv = False
        if sell_st[i] and not np.isnan(ll[i]) and i - int(ll[i]) >= 0:
            j = int(ll[i])
            ref = rv[i - j]
            hi = np.max(rv[i - j + 1:i + 1])
            sv = (hi > ref + dff and rv[i] < ref) or (rv[i] < ref - dff)
        if buy_st[i] and not np.isnan(llb[i]) and i - int(llb[i]) >= 0:
            j = int(llb[i])
            ref = rv[i - j]
            lo_ = np.min(rv[i - j + 1:i + 1])
            bv = (lo_ < ref - dff and rv[i] > ref) or (rv[i] > rhi and i - td >= 0 and rv[i] - rv[i - td] > 0)
        if held == 0 and buy_st[i] and bv and i + 1 < m:
            le[i], held = True, 1
        elif held == 1 and sell_st[i] and sv:
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
