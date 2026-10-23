"""Broker days: two bars in a row closing above the prior 20-bar high on volume above 1.1 x its 10-bar average go long, two below the prior 20-bar low go short; each trade gets a 2 % target and a 15 % stop from its signal close; reversing.
Port of FMZ strategy #475623 "Break of Structure with Volume Confirmation Multi Condition Intelligent Trading Strategy" (BOS and Volume Strategy with Confirmation).

FMZ source id: 475623

Source
    https://www.fmz.com/strategy/475623 (PineScript v5, FMZ last modified 2024-12-20 16:15:43).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 108-168), swing 20 (highest / lowest [1]); volume SMA 10 x 1.1; 2 confirming bars; TP 2 %, SL 15 % from the signal close
    close > highest(high, 20)[1] and highVolume -> bullishCount += 1 (bearish reset) ... ;  bullishCount >= 2 and position_size <= 0 -> entryPrice := close, entry Long
    position_size > 0 -> exit(limit = entryPrice x 1.02, stop = entryPrice x 0.85) every bar;  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the signal close (entryPrice), fixed for the trade: ported as fractions of
      the fill, exact (1e-6 floor). Stated approximation: the source sends them from the fill bar's
      close (they act from the next bar), the house from the fill (as #429494). The count keeps rising
      while the breakout runs, so after a stop or target the strategy re-enters on the next confirmed
      bar; while long a confirmed bar adds nothing. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close as fractions of the fill.
    2 generic: PASS, confirmed breaks of structure on high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.1 x its SMA 10; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_475623_bos_confirmed_volume_2_15pct_bracket_reversal"
FAMILY = "breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.02, 0.05],
    "sl": [0.15, 0.05],
}
DEFAULT_PARAMS = {"swing": 20, "vol_len": 10, "vol_mult": 1.1, "confirm": 2, "tp": 0.02, "sl": 0.15}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["swing"])
    hv = v > v.rolling(int(p["vol_len"])).mean() * float(p["vol_mult"])
    up = ((c > h.rolling(n).max().shift(1)) & hv).to_numpy()
    dn = ((c < lo.rolling(n).min().shift(1)) & hv).to_numpy()
    m = len(up)
    bc, sc = np.zeros(m), np.zeros(m)
    b = s = 0
    for i in range(m):
        if up[i]:
            b, s = b + 1, 0
        elif dn[i]:
            b, s = 0, s + 1
        else:
            b = s = 0
        bc[i], sc[i] = b, s
    k = int(p["confirm"])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(bc >= k, index=ix), false, pd.Series(sc >= k, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
