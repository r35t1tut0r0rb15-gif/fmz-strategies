"""Broker days, long only: OBV rising, the Coppock curve (WMA 10 of ROC 14 + ROC 11) positive and rising and the Chande momentum oscillator 14 above 50 goes long; OBV falling, the Coppock curve negative and falling and the CMO under -50 closes it.
Port of FMZ strategy #442212 "基于OBVCMO和Coppock曲线的交易策略OBV-CMO-and-Coppock-Curve-Based-Trading-Strategy" (RB - OBV Coppock CMO Strategy).

FMZ source id: 442212

Source
    https://www.fmz.com/strategy/442212 (PineScript v4, FMZ last modified 2024-02-20 11:26:46).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 135-172), CMO 14, 50 / -50; Coppock ROC 14 / 11, WMA 10
    buy_signal = obv > obv[1] and coppock > 0 and coppock > coppock[1] and cmo > 50 -> entry Buy
    sell_signal = obv < obv[1] and coppock < 0 and coppock < coppock[1] and cmo < -50 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * OBV adds the volume on up closes and subtracts it on down closes; OBV rising is simply an up close
      on non-zero volume. CMO as Pine's: 100 x (sum of up changes - sum of down changes) / their total over
      14 bars. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, OBV, Coppock curve and CMO agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV direction test; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442212_obv_coppock_cmo_agreement_long_only"
FAMILY = "momentum_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cmo_buy": [50, 30],
    "cmo_period": [14, 9],
}
DEFAULT_PARAMS = {"cmo_period": 14, "roc_long": 14, "roc_short": 11, "wma_len": 10, "cmo_buy": 50, "cmo_sell": -50}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    d = c.diff()
    obv = pd.Series(np.where(d > 0, v, np.where(d < 0, -v, 0.0)), index=c.index).cumsum()
    rl, rs = int(p["roc_long"]), int(p["roc_short"])
    roc = 100 * (c - c.shift(rl)) / c.shift(rl) + 100 * (c - c.shift(rs)) / c.shift(rs)
    cop = _wma(roc, int(p["wma_len"]))
    n = int(p["cmo_period"])
    su, sd = d.clip(lower=0).rolling(n).sum(), (-d).clip(lower=0).rolling(n).sum()
    tot = su + sd
    cmo = 100 * (su - sd) / tot.where(tot != 0)
    buy = ((obv > obv.shift(1)) & (cop > 0) & (cop > cop.shift(1)) & (cmo > float(p["cmo_buy"]))).to_numpy()
    sell = ((obv < obv.shift(1)) & (cop < 0) & (cop < cop.shift(1)) & (cmo < float(p["cmo_sell"]))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
