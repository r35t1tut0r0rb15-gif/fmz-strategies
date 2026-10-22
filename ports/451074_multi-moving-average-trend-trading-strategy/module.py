"""Close crossings over the SMA 9 above the SMA 21 and SMA 200, 3-hour bars, long only, from flat, with a 100-tick bracket from the signal close (the 17:00 close-all never fires on 3-hour bars).
Port of FMZ strategy #451074 "Multi Moving Average Trend Trading Strategy" (Médias Móveis de MarcosJR).

FMZ source id: 451074

Source
    https://www.fmz.com/strategy/451074 (PineScript v5, FMZ last modified 2024-05-11 17:32:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-212), SMA 9 / 21 / 200; stop gain / loss 100 ticks from the signal close; close all at 17:00
    close > sma200 and close > sma21 and crossover(close, sma9) and no open trade -> entry_price = close, entry Compra;  long -> exit(limit = entry + 100 ticks, stop = entry - 100 ticks)
    hour == 17 and minute == 0 and hour[1] < 17 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 100-tick bracket (mintick 0.1 = 10 price units) is re-expressed as sl_stop =
      tp_stop = k_atr x ATR(14) / close of the signal bar, shifted one bar inside stops() and re-based
      on the fill; 0.0286 is the reading against a 3-hour BTC ATR near 350 (interpolated). The exit is
      sent from the fill bar on (active from the fill, as #440797). On UTC-aligned 3-hour bars the
      hour is never 17, so the close-all never fires. Stops on 3-hour bars: mark coarse_bar_stop. Long
      only. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the signal close.
    2 generic: PASS, SMA trend pullback crossings with a tick bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: the 17:00 close-all never fires on 3-hour bars.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_451074_sma9_cross_above_sma21_200_tick_bracket_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.0286, 1.0],
    "ma_medium": [21, 50],
}
DEFAULT_PARAMS = {"k_atr": 0.0286, "ma_medium": 21, "ma_short": 9, "ma_long": 200, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s9 = c.rolling(int(p["ma_short"])).mean()
    le = ((c > c.rolling(int(p["ma_long"])).mean()) & (c > c.rolling(int(p["ma_medium"])).mean())
          & (c > s9) & (c.shift(1) <= s9.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
