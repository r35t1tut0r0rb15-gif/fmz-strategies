"""ChrisMoody MACD histogram turns, broker days: the histogram (MACD 12 / 26 less its SMA 9) crossing above zero goes long,
crossing below goes short (reversing); a long is closed when the histogram falls while above zero, a short when it rises
while at or below zero.
Port of FMZ strategy #434598 "基于MACD指标的双向交易策略MACD-based-Dual-Trading-Strategy" (MACD Strategy).

FMZ source id: 434598

Source
    https://www.fmz.com/strategy/434598 (PineScript v3, FMZ last modified 2023-12-07 17:11:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 123-243), MACD 12 / 26, signal SMA 9; current chart resolution; quantity 1
    hist = macd - sma(macd, 9);  crossover(hist, 0) -> entry long;  crossunder(hist, 0) -> entry short
    hist < hist[1] and hist > 0 -> close long;  hist > hist[1] and hist <= 0 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Use current chart resolution" is on, so the security calls are the chart's own series. The
      closes act on the position held on the bar; an entry on the same bar wins. strategy.entry
      reverses: REVERSAL INTENDED. The fixed quantity 1 is sizing.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 1 stored.
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

NAME = "fmz_434598_macd_hist_turn_exits"
FAMILY = "macd_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 6],
    "slow": [26, 52],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.rolling(int(p["signal"])).mean()
    h1 = hist.shift(1)
    le = ((hist > 0) & (h1 <= 0)).to_numpy()
    se = ((hist < 0) & (h1 >= 0)).to_numpy()
    xl = ((hist < h1) & (hist > 0)).to_numpy()
    xs = ((hist > h1) & (hist <= 0)).to_numpy()
    m = len(le)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if le[i]:
            new = 1
        if se[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
