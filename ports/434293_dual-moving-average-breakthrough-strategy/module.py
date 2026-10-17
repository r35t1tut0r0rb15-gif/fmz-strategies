"""Three long triggers with a fixed bracket, broker days, long only: an EMA 12 / 26 cross up, a MACD 12 / 26 / 9 histogram
cross above zero, or a bar closing more than 8 % above its open goes long (from flat); each trade carries a 5 % stop and
a 40 % target.
Port of FMZ strategy #434293 "Dual Moving Average Breakthrough Strategy" (Volatile Stocks).

FMZ source id: 434293

Source
    https://www.fmz.com/strategy/434293 (PineScript v3, FMZ last modified 2023-12-05 10:46:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 171-218), EMA 12 / 26 (EMA 100 plotted only); MACD 12 / 26 / 9; pump 8 %; SL 5 %, TP 40 % of the average price
    crossover(ema12, ema26) -> entry "Cross" long;  crossover(MACD - ema(MACD, 9), 0) -> entry "MACD" long;  close > open (1 + 8 %) -> entry "Pump" long
    exit each id (stop = avg (1 - 5 %), limit = avg (1 + 40 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding is 0 (one entry), so the first trigger opens the trade and later triggers while
      long are ignored: Opposite entries cannot occur (long only). The three exits share the same
      levels, so one bracket: sl_stop 0.05, tp_stop 0.40 of the fill. Pine sets the levels from the
      bar after the fill (the average price is na on the signal bar); the engine's minute stops can
      act within the fill bar (approximation stated).
    * Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; stops on daily bars: mark coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, average and MACD crosses, a bar-range threshold and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434293 (2 members, best partner #439229, Jaccard 1.000); ND430776 (2 members, best partner #430776, Jaccard 0.798); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434293_ema_macd_pump_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [12, 6],
    "pump": [0.08, 0.04],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "macd_fast": 12, "macd_slow": 26, "macd_sig": 9, "pump": 0.08,
                  "sl_pct": 0.05, "tp_pct": 0.40}


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
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["macd_sig"]), adjust=False).mean()
    x1 = (ef > es) & (ef.shift(1) <= es.shift(1))
    x2 = (delta > 0) & (delta.shift(1) <= 0)
    x3 = c > o * (1 + float(p["pump"]))
    le = (x1 | x2 | x3).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
