"""Three-score trend entries with a 1 % / 2 % bracket, broker days, long only: when at least two of RSI-50 momentum (its EMA
24 over its SMA 24), RSI trend (the SMA 24 of RSI 50 above 45) and price trend (EMA 50 over SMA 50) agree, go long, unless
the position changed on this bar; each trade carries a 1 % stop and a 2 % target.
Port of FMZ strategy #435124 "Momentum Indicator Driven Trend Following Trading Strategy" (I11L Unitrend).

FMZ source id: 435124

Source
    https://www.fmz.com/strategy/435124 (PineScript v5, FMZ last modified 2023-12-12 14:52:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 122-183), mode Unitrend; RSI 50, EMA / SMA 24; risk 1 %, TP factor 2; compounding off, leverage 1
    score = (ema(rsi50, 24) / sma(rsi50, 24) > 1) + (sma(rsi50, 24) / 45 > 1) + (ema(close, 50) / sma(close, 50) > 1)
    score > 1 and not disableAdditionalBuysThisDay -> entry long;  position -> exit(stop = avg (1 - 1 %), limit = avg (1 + 2 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * "disableAdditionalBuysThisDay" is set on any bar where the position size changed and cleared
      once 8 hours have passed since, so on daily bars it only blocks an entry on the bar of a change
      (a fill or an exit). The port tracks the house bracket on bars for that. An entry while long is
      ignored (pyramiding 1). The bracket uses the fill price: sl_stop 0.01, tp_stop 0.02.
    * The capital-based quantity and leverage are sizing. Long only. Stop module: portfolio_kwargs
      {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, RSI and average ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital-based quantity, leverage and compounding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 8-hour re-enable is inert on daily bars except on change bars).
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435124_unitrend_score_bracket"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_pct": [0.01, 0.03],
    "tp_factor": [2.0, 1.0],
}
DEFAULT_PARAMS = {"risk_pct": 0.01, "tp_factor": 2.0}


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
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / 50, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / 50, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    rf, rs = rsi.ewm(span=24, adjust=False).mean(), rsi.rolling(24).mean()
    score = (rf / rs > 1).astype(int) + (rs / 45 > 1).astype(int) + \
        (c.ewm(span=50, adjust=False).mean() / c.rolling(50).mean() > 1).astype(int)
    buy = (score > 1).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    s_, t_ = float(p["risk_pct"]), float(p["risk_pct"]) * float(p["tp_factor"])
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, ei = 0, -1
    for i in range(m):
        changed = pos == 1 and i == ei                     # the entry filled at this bar's open
        if pos == 1 and i >= ei and (lv[i] <= ov[ei] * (1 - s_) or hv[i] >= ov[ei] * (1 + t_)):
            pos, changed = 0, True                         # the bracket closed the trade on this bar
        if pos == 0 and buy[i] and not changed:
            le[i], pos, ei = True, 1, i + 1
    return le


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["risk_pct"]), "tp_stop": float(p["risk_pct"]) * float(p["tp_factor"])}


def portfolio_kwargs(**params):
    return {}
