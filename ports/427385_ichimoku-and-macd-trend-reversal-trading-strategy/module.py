"""The Impeccable, broker days: with the weekly open (3 days back) above the Tenkan line (9-day
mid-range, 2 days back), a MACD (3 / 10 / 9) cross down 3 days earlier buys one unit; with it below,
a MACD cross up 3 days earlier sells one unit. Units net: a buy while short only flattens, a sell
while long only flattens; no trading on weekend days.
Port of FMZ strategy #427385 "Ichimoku and MACD Trend Reversal Trading Strategy".

FMZ source id: 427385

Source
    https://www.fmz.com/strategy/427385 (PineScript v5, FMZ last modified 2023-09-20 15:44:13).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 174-253), Tenkan 9, MACD 3 / 10 / 9, weekends off
    openW3 = request.security(ticker, "W", open)[3]; Tenkan = mid(highest 9, lowest 9)[2]
    long  = openW3 > Tenkan and crossunder(macd, signal)[3] and not long and weekday
    short = openW3 < Tenkan and crossover(macd, signal)[3] and not short and weekday
    strategy.order(buy, qty 1) on long; strategy.order(sell, qty 1) on short

Interpretation choices (Pine rules in SURVEY_README.md, skill section 4)
    * strategy.order nets: the position is -1, 0 or +1 unit; an opposite order flattens, it does not
      reverse. Opposite entries cannot occur (an opposite signal is an exit).
    * Weekly open with lookahead_off: on history only completed weeks are seen. House rule (as #427188):
      a broker week (ISO week of the broker-day date) counts as completed from the first daily bar
      of the next week; the value is then shifted 3 daily bars ([3]).
    * Weekends: dayofweek of the bar in the exchange zone (UTC for the source's Binance pair). On
      broker days the port blocks bars whose broker-day date is a Saturday or Sunday (a Monday
      session that opens on Sunday evening New York time trades).
    * ExitAtEndOfDay / ExitOnFriday apply to intraday charts only (timeframe.isintraday false on
      daily bars); ProfitTarget / StopLoss / ExitAfterBars are inputs no order uses.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the weekly value only once the week completed.
    2 generic: PASS, price comparisons and MACD crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 per order stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); weekend days by the broker-day date; no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427385_impeccable_weekly_open_macd"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "macd_fast": [3, 12],
    "macd_slow": [10, 26],
}
DEFAULT_PARAMS = {"tenkan": 9, "macd_fast": 3, "macd_slow": 10, "macd_smooth": 9, "no_weekends": True}


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


def _completed_week_open(bars, bday):
    iso = bday.isocalendar()
    key = (iso["year"].to_numpy() * 100 + iso["week"].to_numpy())
    wk_open = pd.Series(bars["open"].to_numpy(), index=key).groupby(level=0).first()
    pos_of = {k: j for j, k in enumerate(wk_open.index)}
    vals = wk_open.to_numpy()
    out = np.full(len(key), np.nan)
    for i, k in enumerate(key):
        j = pos_of[k] - 1
        if j >= 0:
            out[i] = vals[j]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    bday = broker_day(bars_df.index)
    w_open = pd.Series(_completed_week_open(bars_df, bday), index=bars_df.index).shift(3)
    n = int(p["tenkan"])
    tenkan = ((h.rolling(n).max() + lo.rolling(n).min()) / 2).shift(2)
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["macd_smooth"]), adjust=False).mean()
    xdn = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).shift(3, fill_value=False)
    xup = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).shift(3, fill_value=False)
    weekday = pd.Series(bday.dayofweek < 5, index=bars_df.index) if p["no_weekends"] else True
    buy = ((w_open > tenkan) & xdn & weekday).to_numpy()
    sell = ((w_open < tenkan) & xup & weekday).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos != 1:
            if pos == -1:
                sx[i] = True
            else:
                le[i] = True
            pos += 1
        elif sell[i] and pos != -1:
            if pos == 1:
                lx[i] = True
            else:
                se[i] = True
            pos -= 1
    idx = bars_df.index
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx), pd.Series(sx, index=idx)


def portfolio_kwargs(**params):
    return {}
