"""MACD(12, 26, 9) crossings with an SMA 25 / 45 gap filter, daily bars: a MACD cross up goes long, a cross down short; a target and stop 0.06 price units from the signal close (re-expressed as
fractions); reversing.
Port of FMZ strategy #443133 "Multiple Moving Average Trading Strategy" (MACD ZLSMA_izumi).

FMZ source id: 443133

Source
    https://www.fmz.com/strategy/443133 (PineScript v5, FMZ last modified 2024-02-29 14:32:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-296), MACD 12 / 26 / 9; SMA 5 / 25 / 45 / 100; gap 0.03 (price units); profit / stop 0.06 (price units); ZLSMA 32 (plot only)
    |sma25 - sma45| > 0.03 and crossover(macd, signal) -> entry long, longProfit = close + 0.06, longStop = close - 0.06;  exit(long, limit = longProfit, stop = longStop)
    |sma25 - sma45| > 0.03 and crossunder -> entry short, shortProfit = close - 0.06, shortStop = close + 0.06;  exit(short, ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 0.03 gap and the 0.06 distances are price units: as fractions of the close at
      the BTC reading of 42000, 7.1e-7 and 1.43e-6 (the bracket closes almost at once, as written),
      re-based on the fill. A new same-side signal while held moves the script's levels, which the port
      does not follow (as #439608). The ZLSMA only plots. strategy.entry reverses: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit gap and bracket -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_443133_macd_cross_sma_gap_unit_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bracket_frac": [1.43e-06, 0.01],
    "gap_frac": [7.1e-07, 0.005],
}
DEFAULT_PARAMS = {"bracket_frac": 1.43e-06, "gap_frac": 7.1e-07, "fast": 12, "slow": 26, "signal": 9}


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    gap = (c.rolling(25).mean() - c.rolling(45).mean()).abs() > float(p["gap_frac"]) * c
    lsig = (gap & (macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    ssig = (gap & (macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    f = float(p["bracket_frac"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - f) or hv[i] >= x * (1 + f):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["bracket_frac"])
    return {"sl_stop": f, "tp_stop": f}


def portfolio_kwargs(**params):
    return {}
