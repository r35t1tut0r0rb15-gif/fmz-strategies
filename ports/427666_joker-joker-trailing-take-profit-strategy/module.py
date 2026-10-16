"""Joker trailing take-profit: SMA 23 crossing above SMA 50 goes long, crossing below goes short; once
price reaches 0.5 % of profit a trailing stop 0.01 % behind the best price takes the profit.
Port of FMZ strategy #427666 "Joker Trailing Take Profit Strategy".

FMZ source id: 427666

Source
    https://www.fmz.com/strategy/427666 (PineScript v5, FMZ last modified 2023-09-23 15:04:20).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 143-187), SMA 23 / 50, TP 0.5 %, trailing 0.01 %
    crossover(fastMA, slowMA) -> entry long; crossunder -> entry short
    TP price = signal-bar close x (1 +- 0.5 %), held while the position is open
    exit(trail_price = TP price, trail_offset = TP price x 0.01 % in ticks) (trailing enabled)

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * The trailing take-profit is ported natively: the house trail
      {"type": "percent", "pct": 0.0001, "anchor": "high_low", "activate_after": 0.005}. Mark
      trailing_stop. Stated approximation: Pine's activation price is 0.5 % from the SIGNAL bar's
      close, the house's 0.5 % from the fill (the next open); the offset is fixed in ticks from the
      TP price in Pine, a percentage of the best price in the house (0.01 % either way).
    * "Enable Trailing" defaults to true and is fixed (the limit variant is a different exit).
    * The short side's nz() fallback multiplies by the price instead of the percentage (a typo),
      but the fallback is never reached once a short is open; ported without it.
    * The date window is dropped (isWithinPeriod is true). Stop module: portfolio_kwargs {}
      (driver D4); REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the trail is a house trail (approximation stated).
    2 generic: PASS, percentages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import pandas as pd

NAME = "fmz_427666_joker_sma_cross_trail_tp"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [23, 10],
    "slow": [50, 100],
    "tp_pct": [0.5, 1.0],
}
DEFAULT_PARAMS = {"fast": 23, "slow": 50, "tp_pct": 0.5, "trail_pct": 0.01}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false.copy(), short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]) / 100, "anchor": "high_low",
                      "activate_after": float(p["tp_pct"]) / 100}}


def portfolio_kwargs(**params):
    return {}
