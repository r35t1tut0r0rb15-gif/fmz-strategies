"""EMA 13 vs EMA 33 side with a near-immediate tick trail and EMA exits, two-day bars: whenever EMA 13 is at or above
EMA 33 and the strategy is not long it goes long (closing a short), and at or below it goes short; while in a trade a
trail two ticks behind the best price is re-placed every bar; EMA 13 rising above EMA 25 closes a short.
Port of FMZ strategy #489653 "双指数均线交叉与尾随止损结合的量化交易策略-Dual-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop-Mechanism" (EMA Crossover (Short Focus with Trailing Stop)).

FMZ source id: 489653

Source
    https://www.fmz.com/strategy/489653 (PineScript v6, FMZ last modified 2025-04-07 13:39:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-233), EMA 13 / 25 / 33, trail offset 2 ticks, trail price high -+ 10
    long = ema13 >= ema33 and position <= 0 -> close short, entry long;  short = ema13 <= ema33 and position >= 0 -> mirror
    position > 0: exit(trail_offset = 2, trail_price = high - 10)   (shorts mirrored with low + 10)
    exitLong = ema13 < ema33 -> close long;  exitShort = ema13 > ema25 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail: activation at the bar's high - 10 (price units), i.e. at once, then 2 ticks behind the best price.
      Ported natively (mark trailing_stop): {"type": "percent", "pct": 0.000007, "anchor": "high_low"} with no
      activation (2 ticks of 0.01 on the author's ETH_USDT at about 3000; judgement before any backtest), as #489737.
    * Every condition bar is an entry (Pine's position gate = the engine ignoring a same-side entry). exitLong implies
      the short condition (a reversal anyway). exitShort is emitted as a short exit on bars without a short entry:
      when both hold, the source enters short from flat and closes a short held at the bar's start; since the trail
      closes nearly every trade within its first bar, the port takes the from-flat reading (stated approximation).
      On EMA 13 == EMA 33 the short (written last) wins. Entries reverse (REVERSAL INTENDED).
    * Stop module: portfolio_kwargs {} (D4). FREQ = "2D" from the backtest header (period 2d): two-day bars from
      broker days in fixed blocks counted from 1970-01-01 (block phase: decision owed), as #426509: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> a fraction of price; the price-unit activation is immediate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 20 % of equity quoted; the trail ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND489653 (2 members, best partner #489737, Jaccard 0.651); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489653_ema13_33_side_tick_trail_2d"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.000007, 0.01],
    "long_ema": [33, 50],
}
DEFAULT_PARAMS = {"short_ema": 13, "mid_ema": 25, "long_ema": 33, "trail_pct": 0.000007}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    em = c.ewm(span=int(p["mid_ema"]), adjust=False).mean()
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    short_c = (es <= el).astype(bool)
    long_c = ((es >= el) & ~short_c).astype(bool)
    short_x = ((es > em) & ~short_c).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, short_x


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
