"""Pullbacks in an uptrend, broker days, long only from flat: a close above the SMA 200 and under the SMA 10 with RSI 3
under 30 goes long, with a 5 % stop and a 20 % target; a close back above the SMA 10 that is under the previous low
closes it.
Port of FMZ strategy #434610 "Moving Average Pullback Trading Strategy" (simple pull back).

FMZ source id: 434610

Source
    https://www.fmz.com/strategy/434610 (PineScript v5, FMZ last modified 2023-12-07 18:09:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-183), SMA 200 / 10, RSI 3 < 30; SL 5 %, TP 20 % of the average price; dates 2000-2099
    close > sma200 and close < sma10 and position_size == 0 and rsi(close, 3) < 30 -> entry long
    exit(stop = avg (1 - 5 %), limit = avg (1 + 20 %));  close > sma10 and close < low[1] and long -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket uses the fill price: sl_stop 0.05, tp_stop 0.20. Entries only from flat
      (position_size == 0): "flat" follows the house bracket on bars and the exit signal. The exit
      needs a close above the SMA 10 and below the previous low, as written. The date filter is
      always true.
    * Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, averages, a short RSI and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434610 (4 members, best partner #435128, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434610_sma_pullback_rsi3_bracket"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_len": [200, 100],
    "sl_pct": [0.05, 0.10],
}
DEFAULT_PARAMS = {"long_len": 200, "short_len": 10, "rsi_len": 3, "rsi_lvl": 30, "sl_pct": 0.05, "tp_pct": 0.20}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ml, ms = c.rolling(int(p["long_len"])).mean(), c.rolling(int(p["short_len"])).mean()
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    buy = ((c > ml) & (c < ms) & (rsi < float(p["rsi_lvl"]))).to_numpy()
    ex = ((c > ms) & (c < lo.shift(1))).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ei = 0, -1
    for i in range(m):
        if pos == 1 and i >= ei:                          # the house bracket from the fill price
            e = ov[ei]
            if lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_):
                pos = 0
        if pos == 1 and i >= ei and ex[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos, ei = True, 1, i + 1
    return le, lx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
