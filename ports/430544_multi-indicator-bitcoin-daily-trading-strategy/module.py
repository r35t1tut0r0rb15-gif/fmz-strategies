"""MACD / RSI / stochastic-RSI daily (CredibleHulk, bennef), broker days: the MACD histogram crossing up through a small
negative level, or RSI 4 crossing up through 30, with stochastic RSI under 57 goes long; the histogram crossing below
zero, or the close falling under its SMA 14 of ohlc4 with stochastic RSI over 57, goes short; 5 % stops each side.
Port of FMZ strategy #430544 "Multi Indicator Bitcoin Daily Trading Strategy" (BTC Daily Strategy BF).

FMZ source id: 430544

Source
    https://www.fmz.com/strategy/430544 (PineScript v4, FMZ last modified 2023-10-30 10:37:58).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-239), MACD 11 / 18 / 6, RSI 4, stochastic RSI 8 / 4, SMA 14 of ohlc4, thresholds -2 / -1 (price units), stops 5 %
    delta = MACD(11, 18) - ema(MACD, 6); rs = rsi(close, 4); k = sma(stoch(rs, rs, rs, 8), 4)
    long = (crossover(delta, -2) or crossover(rs, 30)) and k < 57 -> entry long
    short = crossunder(delta, 0) or (crossunder(close - sma(ohlc4, 14), -1) and k > 57) -> entry short
    exit(stop = avg x 0.95) for longs, (stop = avg x 1.05) for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the histogram level -2 and the distance level -1 are price units; they become
      -0.002 and -0.001 x Wilder ATR(14) of the same bar (2 and 1 USD on daily BTC, about 0.002 /
      0.001 ATR).
    * When both signals fire on one bar the short, written second, wins (the long is not emitted).
    * The stops are 5 % from the average price = the fill: sl_stop 0.05. testPeriod() is always true.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed percentage stop.
    2 generic: ADAPT, the price-unit thresholds -> ATR fractions.
    3 crypto-exchange-only: no ("Bitcoin" in the corpus title only; exchange pair in the header).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430544_btc_daily_macd_rsi_srsi"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "rsi_threshold": [30, 20],
    "srsi_threshold": [57, 50],
}
DEFAULT_PARAMS = {"rsi_threshold": 30, "rsi_length": 4, "srsi_length": 8, "srsi_smooth": 4, "srsi_threshold": 57,
                  "length": 14, "dma_atr": -0.001, "fast": 11, "slow": 18, "macd_len": 6, "macd_atr": -0.002,
                  "loss_tol": 5.0}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["macd_len"]), adjust=False).mean()
    rs = _rsi(c, int(p["rsi_length"]))
    n = int(p["srsi_length"])
    ll, hh = rs.rolling(n).min(), rs.rolling(n).max()
    k = (100 * (rs - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["srsi_smooth"])).mean()
    atr = _atr(bars_df, ATR_LEN)
    thr = c - ((o + h + lo + c) / 4).rolling(int(p["length"])).mean()
    zero = pd.Series(0.0, index=c.index)
    long_e = ((_xo(delta, atr * p["macd_atr"]) | _xo(rs, zero + p["rsi_threshold"])) & (k < p["srsi_threshold"]))
    short_e = (_xu(delta, zero) | (_xu(thr, atr * p["dma_atr"]) & (k > p["srsi_threshold"])))
    long_e = (long_e & ~short_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["loss_tol"]) / 100}


def portfolio_kwargs(**params):
    return {}
