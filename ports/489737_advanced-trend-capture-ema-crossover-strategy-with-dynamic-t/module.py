"""EMA 13 vs EMA 33 side with a near-immediate tick trail, broker days: whenever EMA 13 is at or above EMA 33 and the
strategy is not long it goes long (closing a short), and at or below it goes short; while in a trade a trail two
ticks behind the best price is re-placed every bar, which closes the trade on the first small retrace (the EMA exits
are never reached, as written); the next bar re-enters if the EMA side still holds.
Port of FMZ strategy #489737 "高效趋势捕捉型指数移动平均线交叉与动态追踪止损策略-Advanced-Trend-Capture-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop" (EMA Crossover (New Trailing Stop)).

FMZ source id: 489737

Source
    https://www.fmz.com/strategy/489737 (PineScript v6, FMZ last modified 2025-04-08 10:23:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 245-313), EMA 13 / 25 / 33, trail offset 2 ticks, trail price high -+ 10
    long = ema13 >= ema33 and position <= 0 -> close short, entry long;  short = ema13 <= ema33 and position >= 0 -> mirror
    position > 0: exit(trail_offset = 2, trail_price = high - 10); isExiting = true   (shorts mirrored with low + 10)
    exitLong (ema13 < ema33) / exitShort (ema13 > ema25) only when not isExiting; isExiting resets at every bar close

Interpretation choices (Pine rules in SURVEY_README.md)
    * While a position is held the trail block runs first and sets isExiting, so the EMA exits after it never run:
      dead code, as written (not emitted).
    * The trail: activation at the bar's high - 10 (price units), i.e. at once, then 2 ticks behind the best price.
      Ported natively (mark trailing_stop): {"type": "percent", "pct": 0.000007, "anchor": "high_low"} with no
      activation. Stated approximation: 2 ticks of 0.01 on the author's ETH_USDT at about 3000 are 0.0007 % of price
      (judgement before any backtest); re-placing it every bar changes nothing once it is active.
    * Every condition bar is an entry (Pine's position gate = the engine ignoring a same-side entry); after a trail
      exit the next bar re-enters. On a bar with EMA 13 == EMA 33 both blocks run and the short (written last) wins.
      Entries reverse (REVERSAL INTENDED). slippage = 5 in strategy() is a cost (not in the module).
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> a fraction of price; the price-unit activation is immediate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 20 % of equity quoted; the trail ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND489653 (2 members, best partner #489653, Jaccard 0.651); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489737_ema13_33_side_tick_trail"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.000007, 0.01],
    "long_ema": [33, 50],
}
DEFAULT_PARAMS = {"short_ema": 13, "long_ema": 33, "trail_pct": 0.000007}


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
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    short_c = (es <= el).astype(bool)
    long_c = ((es >= el) & ~short_c).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
