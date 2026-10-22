"""Weekly MACD histogram direction with daily breakouts, daily bars: with last week's histogram above the week before's, the close crossing over the 3-week EMA of past weekly closes goes long; with it below,
the EMA 50 crossing under the EMA 150 goes short; a 100-point loss from the fill or the close crossing under the EMA 60 closes a long, the mirror closes a short; reversing.
Port of FMZ strategy #445788 "MACDEMA多时间尺度突破策略MACDEMA-Multi-Timeframe-Breakout-Strategy" (Last week MACD+ 15day, 30day break through, by Ho.J).

FMZ source id: 445788

Source
    https://www.fmz.com/strategy/445788 (PineScript v5, FMZ last modified 2024-03-22 11:13:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-246), weekly MACD 12 / 26 / 9 (hist[1] - hist[2]); weekly EMA 3 of close[1] (EMA 1 / 6 plot only); daily EMA 50 / 60 / 150; loss 100 points; capital 30000, commission 7.5 per order; dates (always true)
    histDiff = security(W, hist[1]) - security(W, hist[2]) (lookahead on);  lastWeekEMA2 = security(W, ema(close[1], 3)) (lookahead on)
    crossover(close, lastWeekEMA2) and histDiff > 0 -> entry Buy;  (long and avg - close >= 100) or crossunder(close, ema60) -> close Buy
    crossunder(ema50, ema150) and histDiff < 0 -> entry Sell;  (short and close - avg >= 100) or crossover(ema50, ema60) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly requests use lookahead with [1] / close[1] inside, the non-repainting form: each daily
      bar sees the last completed broker week's histogram and the week before's, and the EMA 3 of
      closes up to the last completed week, built from the module's own bars (broker weeks Monday to
      Friday by broker-day label). Criterion 2: the 100-point loss is a fraction of the fill price,
      0.00238 (100 against BTC near 42000); it is a bar-close test against the fill (the next open after
      the signal) and closes at the next open. "a and b or c" binds as (a and b) or c, so the EMA
      crossing closes a held position whatever its loss. Calls run in order; a close then the opposite
      entry on one bar is one reversal. The Monday label only plots. REVERSAL INTENDED. The capital and
      per-order commission are sizing / costs (not ported). FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, weekly MACD direction with daily EMA breakouts and a loss exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital stored; the cash commission is a cost, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_445788_weekly_macd_dir_daily_ema_break_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "loss_frac": [0.00238, 0.01],
    "week_ema": [3, 6],
}
DEFAULT_PARAMS = {"loss_frac": 0.00238, "week_ema": 3, "short_ema": 50, "medium_ema": 60, "long_ema": 150}


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
    o, c = bars_df["open"], bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wc = c.groupby(week).last()
    wm = wc.ewm(span=12, adjust=False).mean() - wc.ewm(span=26, adjust=False).mean()
    wh = wm - wm.ewm(span=9, adjust=False).mean()
    wdiff = wh.shift(1) - wh.shift(2)                       # last completed week minus the week before
    wema = wc.shift(1).ewm(span=int(p["week_ema"]), adjust=False).mean()
    hd = wdiff.reindex(week).to_numpy()
    e2 = pd.Series(wema.reindex(week).to_numpy(), index=c.index)
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    em = c.ewm(span=int(p["medium_ema"]), adjust=False).mean()
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    c1 = c.shift(1)
    with np.errstate(invalid="ignore"):
        buy = ((c > e2) & (c1 <= e2.shift(1))).to_numpy() & (hd > 0)
        sell = ((es < el) & (es.shift(1) >= el.shift(1))).to_numpy() & (hd < 0)
    xu_med = ((c < em) & (c1 >= em.shift(1))).to_numpy()
    xo_med = ((es > em) & (es.shift(1) <= em.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lf = float(p["loss_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fp = 0, np.nan
    for i in range(m):
        new = pos
        if buy[i] and pos != 1:
            le[i], new = True, 1
        if pos == 1 and new == 1 and ((cv[i] - fp <= -lf * fp) or xu_med[i]):
            lx[i], new = True, 0
        if sell[i] and new != -1:
            se[i], lx[i], new = True, False, -1     # a close then the entry is one reversal
        if pos == -1 and new == -1 and ((cv[i] - fp >= lf * fp) or xo_med[i]):
            sx[i], new = True, 0
        if new != pos and new != 0:
            fp = ov[i + 1] if i + 1 < m else np.nan  # the fill: the next bar's open
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
