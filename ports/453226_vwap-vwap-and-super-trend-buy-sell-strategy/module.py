"""Broker days: the supertrend (2 x ATR 10 on hl2) in its up state with the close above the bar's own hl2 goes long, the down state with the close under hl2 goes short, alternating (a buy only after a sell and vice versa); reversing.
Port of FMZ strategy #453226 "VWAP与超级趋势买卖策略-VWAP-and-Super-Trend-Buy-Sell-Strategy" (VWAPST (VWAP and Super Trend Buy/Sell Strategy)).

FMZ source id: 453226

Source
    https://www.fmz.com/strategy/453226 (PineScript v5, FMZ last modified 2024-06-03 10:45:14).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 90-145), VWAP source hl2; ATR 10, multiplier 2
    TUp := close[1] > TUp[1] ? max(Up, TUp[1]) : Up;  TDown := close[1] < TDown[1] ? min(Dn, TDown[1]) : Dn;  Trend := close > TDown[1] ? 1 : close < TUp[1] ? -1 : Trend[1]
    buysignal = not previousBuysignal and Trend == 1 and close > vwap(hl2) -> entry Buy;  sellsignal = not previousSellsignal and Trend == -1 and close < vwap -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * On daily bars the session VWAP restarts every bar (each broker day is its own session), so it is
      the bar's hl2 and volume cancels out (held for volume, not used). The flags allow a buy only after a
      sell and a sell only after a buy. The supertrend starts in the up state (Trend na -> 1). REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, supertrend state with the bar's own midpoint.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the VWAP restarts each day.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453226_supertrend_state_close_vs_hl2_alternating_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 20],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"period": 10, "mult": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["period"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    mult = float(p["mult"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    t_up = t_dn = np.nan
    trend = None
    prev_buy = prev_sell = False
    pos = 0
    for i in range(m):
        up, dn = hl2[i] - mult * atr[i], hl2[i] + mult * atr[i]
        p_up, p_dn = t_up, t_dn
        t_up = up if np.isnan(p_up) else (max(up, p_up) if cv[i - 1] > p_up else up)
        t_dn = dn if np.isnan(p_dn) else (min(dn, p_dn) if cv[i - 1] < p_dn else dn)
        if trend is None:
            trend = 1
        elif cv[i] > p_dn:
            trend = 1
        elif cv[i] < p_up:
            trend = -1
        buy = (not prev_buy) and trend == 1 and cv[i] > hl2[i]
        sell = (not prev_sell) and trend == -1 and cv[i] < hl2[i]
        if buy:
            prev_buy, prev_sell = True, False
        elif sell:
            prev_buy, prev_sell = False, True
        if buy and pos != 1:
            le[i], pos = True, 1
        elif sell and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
