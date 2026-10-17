"""MACD crosses with RSI extremes inside a London window, 1-minute bars: between 06:59 and 15:59 a MACD 12 / 26 / 9 line
crossing above its signal with the RSI 14 under 35 goes long, a cross below with the RSI over 65 goes short; always in
after the first signal.
Port of FMZ strategy #433430 "基于MACD和RSI的交易策略London-MACD-RSI-Bitcoin-Trading-Strategy" (London MACD RSI Strategy -1H BTC).

FMZ source id: 433430

Source
    https://www.fmz.com/strategy/433430 (PineScript v5, FMZ last modified 2023-11-27 15:44:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 136-172), London 06:59-15:59 (exchange clock); MACD 12 / 26 / 9; RSI 14, 65 / 35
    in_london = time between today's 06:59 and 15:59 (exchange time zone)
    crossover(macd, signal) and rsi < 35 and in_london -> entry long;  crossunder and rsi > 65 and in_london -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock times (C6): timestamp(year, month, dayofmonth, h, m) uses the exchange time zone; on the
      header's BTC_USDT that is UTC. The grid also declares Europe/London (the script's "London"
      hours, DST by the zone). A bar belongs to the window when it opens inside it (both ends
      included). ta.macd's signal is an EMA.
    * strategy.entry reverses: REVERSAL INTENDED. The title's 1-hour chart is not the header's period:
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; clock-time window.
    2 generic: PASS, MACD crosses and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 06:59-15:59 entry window, in UTC (header) or Europe/London (grid), DST by the zone; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433430_london_macd_rsi"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tz": ["UTC", "Europe/London"],
    "rsi_band": [35, 45],
}
DEFAULT_PARAMS = {"tz": "UTC", "rsi_band": 35, "start_min": 419, "end_min": 959, "fast": 12, "slow": 26,
                  "signal": 9, "rsi_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    loc = bars_df.index.tz_convert(str(p["tz"]))
    mins = np.asarray(loc.hour * 60 + loc.minute)
    win = (mins >= int(p["start_min"])) & (mins <= int(p["end_min"]))
    band = float(p["rsi_band"])
    lc = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r < band)).to_numpy() & win
    sc = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r > 100 - band)).to_numpy() & win
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lc, index=ix), false, pd.Series(sc, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
