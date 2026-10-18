"""EMA 10 / 50 crossings gated by the RSI, broker days: a bullish crossing with the RSI under 70 goes long; a bearish crossing with the RSI over 30 goes short; the opposite crossing closes each side.
Port of FMZ strategy #436527 "基于EMA交叉的趋势转向交易策略Trend-Reversal-Trading-Strategy-Based-on-EMA-Crossover" (Trend Change with EMA Entry/Exit - Intraday).

FMZ source id: 436527

Source
    https://www.fmz.com/strategy/436527 (PineScript v5, FMZ last modified 2023-12-25 15:12:46).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 123-159), EMA 10 / 50, RSI 14, limits 70 / 30
    is_uptrend = crossover(ema10, ema50);  is_downtrend = crossunder(ema10, ema50);  is_trending = change(is_uptrend) != 0 or change(is_downtrend) != 0
    enter_long = is_uptrend and rsi < 70 and is_trending;  exit_long = is_downtrend and is_trending;  enter_short = is_downtrend and rsi > 30 and is_trending;  exit_short = is_uptrend and is_trending
    entry Buy, close Buy, entry Sell, close Sell in that order

Interpretation choices (Pine rules in SURVEY_README.md)
    * A crossing is a one-bar event, so its change against the previous bar is always true and is_trending
      only removes the first bar. The four rules of one bar are filled at the next open in the script's
      call order; a close only acts on a position of its own side. A bullish crossing with the RSI at
      70 or more still closes a short. REVERSAL INTENDED. The default quantity is sizing. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, crossings gated by an RSI side test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_436527_ema_cross_rsi_gate"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "rsi_len": 14, "overbought": 70, "oversold": 30}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna()).to_numpy()
    cu = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False).to_numpy()
    cd = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False).to_numpy()
    ob, os_ = float(p["overbought"]), float(p["oversold"])
    m = len(c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if i > 0:                        # fills at this bar's open, in the script's call order
                for op in ops:
                    if op == "eL" and pos <= 0:
                        pos = 1
                    elif op == "eS" and pos >= 0:
                        pos = -1
                    elif op == "XL" and pos > 0:
                        pos = 0
                    elif op == "XS" and pos < 0:
                        pos = 0
            held[i] = pos
            ops = []
            if cu[i] and rsi[i] < ob:
                ops.append("eL")
            if cd[i]:
                ops.append("XL")
            if cd[i] and rsi[i] > os_:
                ops.append("eS")
            if cu[i]:
                ops.append("XS")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
