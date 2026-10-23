"""Broker days: the EMA 80 of a 200-bar Chaikin money flow crossing over its EMA 160 goes long one bar later, crossing under goes short one bar later; each with a 3 % stop and a 5 % target from the entry; reversing.
Port of FMZ strategy #453670 "基于Chaikin资金流量CMF指标策略This-strategy-generates-trading-signals-based-on-the-Chaikin-Money-Flow-CMF" (CASHISKING (Chaikin money flow EMA cross)).

FMZ source id: 453670

Source
    https://www.fmz.com/strategy/453670 (PineScript v5, FMZ last modified 2024-06-07 17:05:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 93-163), CMF 200; EMA 80 / 160 of the CMF; SL 3 %, TP 5 %
    cmf = sma(clv x volume, 200) / sma(volume, 200);  crossover(ema80(cmf), ema160(cmf)) -> crossOverCount := 0, then +1 each bar;  crossOverCount == 2 -> entry Buy;  crossunder mirror -> entry Sell
    position > 0 -> exit("Stop", "Buy", stop = avg x 0.97, limit = avg x 1.05);  position < 0 -> exit("Stop", "Sell", stop = avg x 1.03, limit = avg x 0.95)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counter is set to 0 and incremented on the crossing bar itself, so the entry comes on the
      bar after the crossing (count 2). A bar with high == low has no CLV in Pine (na), which makes the
      200-bar SMA na while it is in the window; the port counts such bars as 0 (they are rare on daily
      bars). The bracket is a level from the average (fill) price, sent from the fill bar's close; the port
      arms it at the fill, as fixed fractions. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed 3 % / 5 % bracket from the fill.
    2 generic: PASS, money-flow EMA crossings, entered one bar later.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the 200-bar Chaikin money flow; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_453670_cmf200_ema80_160_cross_delayed_pct_bracket_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cmf_period": [200, 50],
    "ema_fast": [80, 20],
}
DEFAULT_PARAMS = {"cmf_period": 200, "ema_fast": 80, "ema_slow": 160, "sl": 0.03, "tp": 0.05}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    rng = h - lo
    clv = ((c - lo) - (h - c)) / rng.where(rng != 0)
    n = int(p["cmf_period"])
    sv = v.rolling(n).mean()
    cmf = (clv * v).fillna(0.0).rolling(n).mean() / sv.where(sv != 0)
    ef = cmf.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = cmf.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    x_up = ((ef > es) & (ef.shift(1) <= es.shift(1))).to_numpy()
    x_dn = ((ef < es) & (ef.shift(1) >= es.shift(1))).to_numpy()
    m = len(x_up)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cu = cd = None
    for i in range(m):
        if x_up[i]:
            cu = 0
        if x_dn[i]:
            cd = 0
        if cu is not None:
            cu += 1
        if cd is not None:
            cd += 1
        if cu == 2:
            le[i], cu = True, None
        if cd == 2:
            se[i], cd = True, None
    lg = pd.Series(le & ~se, index=bars_df.index)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, pd.Series(se, index=bars_df.index), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
