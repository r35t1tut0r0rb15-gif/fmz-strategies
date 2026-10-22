"""MACD (5, 13, 5) crossings with RSI filters, broker days: a MACD cross up with the RSI 14 not over 70 goes long, a cross down with it not under 30 goes short (both on a bar whose close differs from the
previous one); a close crossing over its open closes a long, crossing under it closes a short; reversing.
Port of FMZ strategy #439717 "基于MACD和RSI的趋势追踪交易策略Trend-Following-Trading-Strategy-Based-on-MACD-and-RSI" (Al-Sat Sinyali ve Teyidi).

FMZ source id: 439717

Source
    https://www.fmz.com/strategy/439717 (PineScript v5, FMZ last modified 2024-01-23 12:03:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-169), MACD 5 / 13 / 5; RSI 14, 70 / 30
    buy = crossover(macd, signal) and not rsi > 70;  sell = crossunder and not rsi < 30;  if buy and close[1] != close: entry Buy;  if sell and close[1] != close: entry Sell
    close Buy when crossover(close, open);  close Sell when crossunder(close, open)

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossover(close, open) is a close above its open after a bar whose close was not above its open.
      The closes act on the position held at the bar close: a close of the side just reversed out of
      meets no position and the reversal stands (as #438020); a held position meeting its close ends
      flat. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings, RSI and candle crossings.
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

NAME = "fmz_439717_macd5_13_rsi_filter_candle_close"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 12],
    "slow": [13, 26],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 13, "signal": 5, "rsi_len": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    moved = c.shift(1) != c
    buy = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & ~(r > 70) & moved).to_numpy()
    sell = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & ~(r < 30) & moved).to_numpy()
    xb = ((c > o) & (c.shift(1) <= o.shift(1))).to_numpy()
    xs = ((c < o) & (c.shift(1) >= o.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and pos != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if pos == 1 and xb[i] and new == 1:
            new = 0
        if pos == -1 and xs[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
