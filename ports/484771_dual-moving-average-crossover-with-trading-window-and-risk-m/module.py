"""SMA 10 / 25 crossings in the second half of each hour from 08:30 to 14:59 UTC, 1-minute bars: the up-cross goes long with a 50-tick stop and target read as 0.3125 %, the down-cross goes short and (with the source's long-side bracket) is closed at the next open after its fill; everything closes at 15:00 UTC.
Port of FMZ strategy #484771 "Dual Moving Average Crossover with Trading Window and Risk Management Strategy" (Custom MACrossOver).

FMZ source id: 484771

Source
    https://www.fmz.com/strategy/484771 (PineScript v5, FMZ last modified 2025-03-04 10:59:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 253-303), SMA 10 / 25; stop 50 ticks; target 50 ticks; quantity 2; window hour >= 8 and minute >= 30 and hour < 15; close-all at 15:00; MPL 2.0 notice (szapatamejia193)
    window and crossover(sma10, sma25) -> entry Long, entry price := close;  window and crossunder -> entry Short
    long -> exit(stop = entry - 50 ticks, limit = entry + 50 ticks);  short -> exit(stop = entry - 50 ticks, limit = entry + 50 ticks);  15:00 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute read the chart exchange's zone, UTC for the header's Binance pair: as written the
      window needs minute >= 30 in every hour, so only minutes 30-59 of 08:00-14:59 UTC qualify (fixed
      UTC, no DST).
    * Criterion 2: 50 ticks on the header's SOL_USDT (tick 0.01, about 160 USDT) is read as 3.125e-03 of
      the price (as #458242 at the header's prices). The long bracket is sent from the fill bar's close
      around the signal close; it is ported as fixed fractions of the fill, active from the fill bar (as
      #440797). As written (intended version owed) the short gets the same below / above levels, a buy
      stop under the price and a buy limit over it, both marketable, so a short closes at the open after
      its fill bar (as #439872).
    * The 15:00 UTC close-all is an exit signal on that bar. An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The quantity 2 is sizing. The
      MPL 2.0 notice is kept with the verbatim copy (ported, stated). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket as fractions of the fill.
    2 generic: ADAPT, 50 ticks read as a fraction at SOL 160.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: quantity 2 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: window minutes 30-59 of 08:00-14:59 UTC, close-all at 15:00 UTC (fixed UTC, no DST; the header exchange's time zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484771_sma10_25_cross_utc_half_hour_window_tick_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
SESSION_TZ = "UTC"  # hour / minute read the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "fast_length": [10, 5],
    "slow_length": [25, 50],
}
DEFAULT_PARAMS = {"fast_length": 10, "slow_length": 25, "bracket_frac": 3.125e-03}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast_length"])).mean()
    s = c.rolling(int(p["slow_length"])).mean()
    loc = bars_df.index.tz_convert(SESSION_TZ)
    hr, mn = np.asarray(loc.hour), np.asarray(loc.minute)
    win = pd.Series((hr >= 8) & (mn >= 30) & (hr < 15), index=c.index)
    close_all = pd.Series((hr == 15) & (mn == 0), index=c.index)
    le = win & (f > s) & (f.shift(1) <= s.shift(1))
    se = win & (f < s) & (f.shift(1) >= s.shift(1)) & ~le
    return le, se, close_all


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, xa = _signals(bars_df, p)
    sf = se.shift(1, fill_value=False)
    lx = xa
    sx = sf | xa                               # the marketable same-side bracket of a short
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _signals(bars_df, p)
    lf = le.shift(1, fill_value=False)
    q = float(p["bracket_frac"])
    f = pd.Series(q, index=bars_df.index).shift(1).where(lf)
    return {"sl_stop": f, "tp_stop": f.copy()}


def portfolio_kwargs(**params):
    return {}
