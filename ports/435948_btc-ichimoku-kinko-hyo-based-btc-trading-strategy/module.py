"""Ichimoku votes, broker days, long only: a close crossing over the Kijun after six bars of a steady Kijun slope and over both spans, a Chikou
cross within eight bars of the last sell vote, or an RSI rebound from oversold goes long; the mirror conditions close the long.
Port of FMZ strategy #435948 "基于一目均线系统的BTC交易策略Ichimoku-Kinko-Hyo-Based-BTC-Trading-Strategy" (My Ichimoku Strat v2).

FMZ source id: 435948

Source
    https://www.fmz.com/strategy/435948 (PineScript v3, FMZ last modified 2023-12-20 13:34:08).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 172-249), Kijun 26, Tenkan 9, span B 52 (SMA of hl2), Kijun slope look-back 6, RSI 14 with 40 / 60 and 30 / 70 limits
    buy2 = crossover(close, kijun) and (rising(kijun, 6) or falling(kijun, 6));  buy3 = close > spanA and close > spanB (undisplaced);  buy1 = crossover(close, close[26])
    counters: buyCompteur = 1 on buy2 or buy3, then +1 each bar while > 0, reset to -1 on sell2 or sell3 (sellCompteur mirrors)
    buyRSI = crossover(rsi, 40) and close > tenkan and rsi[5] < 30 and rsi - rsi[1] > 5
    buy = buy2 and buy3 or (buy1 and sellCompteur <= 8) or buyRSI;  sell = sell2 and sell3 or (sell1 and buyCompteur <= 8) or sellRSI;  entry long (buy), close (sell)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are the plain averages without displacement, as written. rising(x, 6) means x grew on
      each of the last six bars. The counters are followed in a loop. A bar that both buys and sells
      leaves the position flat (the entry is sent first, then the close), so the entry is dropped. The
      date window (from 1 March 2018) is the author's backtest window: dropped. Long only. The fixed
      size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines and an RSI rebound.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed order size, commission and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434984 (2 members, best partner #434984, Jaccard 0.687); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435948_ichimoku_votes_long"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kijun_lag": [6, 4],
    "kijun_len": [26, 20],
}
DEFAULT_PARAMS = {"kijun_lag": 6, "kijun_len": 26, "tenkan_len": 9, "span_b_len": 52, "chikou": 26, "rsi_len": 14}


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


def _monotone(x, n, up):
    ok = pd.Series(True, index=x.index)
    for k in range(n):
        d = x.shift(k) - x.shift(k + 1)
        ok = ok & ((d > 0) if up else (d < 0))
    return ok


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    kijun = hl2.rolling(int(p["kijun_len"])).mean()
    tenkan = hl2.rolling(int(p["tenkan_len"])).mean()
    span_a = (kijun + tenkan) / 2
    span_b = hl2.rolling(int(p["span_b_len"])).mean()
    lag = int(p["kijun_lag"])
    steady = _monotone(kijun, lag, True) | _monotone(kijun, lag, False)
    buy2 = ((c > kijun) & (c.shift(1) <= kijun.shift(1)) & steady).fillna(False).to_numpy()
    sell2 = ((c < kijun) & (c.shift(1) >= kijun.shift(1)) & steady).fillna(False).to_numpy()
    buy3 = ((c > span_a) & (c > span_b)).fillna(False).to_numpy()
    sell3 = ((c < span_a) & (c < span_b)).fillna(False).to_numpy()
    ch26 = c.shift(int(p["chikou"]))
    buy1 = ((c > ch26) & (c.shift(1) <= ch26.shift(1))).fillna(False).to_numpy()
    sell1 = ((c < ch26) & (c.shift(1) >= ch26.shift(1))).fillna(False).to_numpy()
    n = int(p["rsi_len"])
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=c.index)
    buy_rsi = ((rsi > 40) & (rsi.shift(1) <= 40) & (c > tenkan) & (rsi.shift(5) < 30) & ((rsi - rsi.shift(1)) > 5)).fillna(False).to_numpy()
    sell_rsi = ((rsi < 60) & (rsi.shift(1) >= 60) & (c < tenkan) & (rsi.shift(5) > 70) & ((rsi.shift(1) - rsi) > 5)).fillna(False).to_numpy()
    m = len(buy2)
    buy_c, sell_c = -1, -1
    buy_sig, sell_sig = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(m):
        b_c = buy_c
        s_c = sell_c
        # counters (the script updates both with the pre-update values of the other side)
        nb = 1 if (buy2[i] or buy3[i]) else b_c
        nb = nb + 1 if nb > 0 else nb
        if sell2[i] or sell3[i]:
            nb = -1
        ns = 1 if (sell2[i] or sell3[i]) else s_c
        ns = ns + 1 if ns > 0 else ns
        if buy2[i] or buy3[i]:
            ns = -1
        buy_c, sell_c = nb, ns
        sell_sig[i] = (sell2[i] and sell3[i]) or (sell1[i] and buy_c <= 8) or sell_rsi[i]
        buy_sig[i] = (buy2[i] and buy3[i]) or (buy1[i] and sell_c <= 8) or buy_rsi[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    b, s = pd.Series(buy_sig, index=ix), pd.Series(sell_sig, index=ix)
    return (b & ~s), s, false, false.copy()


def portfolio_kwargs(**params):
    return {}
