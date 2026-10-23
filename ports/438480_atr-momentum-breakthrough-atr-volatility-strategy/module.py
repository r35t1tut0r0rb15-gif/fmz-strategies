"""One-minute bars: the SMA 50 crossing over the SMA 200 with the close under the session VWAP goes long, crossing under with the close over the VWAP goes short; an opposite crossing without an entry closes the position; only shorts carry a bracket (3-tick stop, 5-tick target); reversing.
Port of FMZ strategy #438480 "动量突破ATR波动率策略Momentum-Breakthrough-ATR-Volatility-Strategy" (Simple Moving Averages).

FMZ source id: 438480

Source
    https://www.fmz.com/strategy/438480 (PineScript v5, FMZ last modified 2024-01-12 13:50:44).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 157-196), SMA 50 / 200; vwap(close); exit profit 5 / loss 3 ticks under one shared id
    longCondition = crossover(sma50, sma200) and vwap > close -> entry Long;  shortCondition = crossunder(sma50, sma200) and vwap < close -> entry Short
    close(Long) when crossunder(sma50, sma200);  close(Short) when crossover;  exit("Take Profit / Stop Loss", "Long", profit = 5, loss = 3);  exit("Take Profit / Stop Loss", "Short", profit = 5, loss = 3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits share one id, so the second call (from_entry "Short") replaces the first every bar:
      only shorts get the bracket, longs end by the opposite crossing (as #435894; weird case). profit /
      loss are ticks from the entry price: on the header's BTC_USDT (0.1 tick, about 44000 USD in the
      2024-01-04 .. 01-11 window) 0.5 / 0.3 USD, ported as fractions of the fill 1.14e-5 / 6.8e-6 (as
      #437390); the bracket is fixed at the fill, exactly as written. vwap(close) is the session VWAP,
      anchored at the broker-day start (as earlier ports). A close acts only on a position the bar's
      entries leave unchanged. The RSI, DMI and ATR feed bar colours only. REVERSAL INTENDED. No sizing
      code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed short-only tick bracket from the fill.
    2 generic: PASS, SMA 50 / 200 crossings against the session VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only; tick distances converted at the source's BTC price).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438480_sma50_200_cross_vwap_short_tick_bracket_1m_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "tp": 1.13636e-05, "sl": 6.81818e-06}  # 0.5 / 0.3 USD at 44000


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    co = (f > s) & (f.shift(1) <= s.shift(1))
    cu = (f < s) & (f.shift(1) >= s.shift(1))
    le = co & (vwap > c)
    se = cu & (vwap < c)
    return le, cu & ~se, se, co & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    short_fill = se.shift(1, fill_value=False)          # only the 'Short' entry keeps the shared exit
    sl_f = pd.Series(float(p["sl"]), index=bars_df.index).where(short_fill)
    tp_f = pd.Series(float(p["tp"]), index=bars_df.index).where(short_fill)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
