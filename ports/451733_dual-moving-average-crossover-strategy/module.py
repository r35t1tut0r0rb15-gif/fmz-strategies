"""SMA 50 / 200 golden and death crosses from flat, daily bars: a golden cross while flat goes long and a death cross while flat goes short, each with a 2 % stop from the signal close; the opposite cross closes the trade without reversing it.
Port of FMZ strategy #451733 "Dual Moving Average Crossover Strategy" (Basic Moving Average Crosses).

FMZ source id: 451733

Source
    https://www.fmz.com/strategy/451733 (PineScript v5, FMZ last modified 2024-05-17 15:48:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-157), SMA 50 / 200 (useSma true); stop 2 % of the signal close
    flat and golden cross -> entry Buy, exit(stop = close x 0.98);  flat and death cross -> entry Sell, exit(stop = close x 1.02)
    long and death cross -> close Buy;  short and golden cross -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop levels are fixed on the signal bar from its close: ported as the fixed fraction 0.02
      of the fill (as #437751). Entries only from flat: a cross that closes a trade opens nothing, so
      a short (long) comes only on a death (golden) cross met while flat, after a stop. The loop
      follows the stop on each bar's low / high so that the flat test lines up. Opposite entries
      cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-close stop as a fixed fraction.
    2 generic: PASS, golden / death crosses from flat.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_451733_sma50_200_cross_from_flat_2pct_stop"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "quick": [50, 20],
    "slow": [200, 100],
    "sl_pct": [0.02, 0.05],
}
DEFAULT_PARAMS = {"quick": 50, "slow": 200, "sl_pct": 0.02}


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


def _run(bars_df, p):
    c = bars_df["close"]
    q, s = c.rolling(int(p["quick"])).mean(), c.rolling(int(p["slow"])).mean()
    gold = ((q > s) & (q.shift(1) <= s.shift(1))).to_numpy()
    death = ((q < s) & (q.shift(1) >= s.shift(1))).to_numpy()
    sl = float(p["sl_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - sl):
            pos = 0
        elif pos == -1 and i >= entry_i and hv[i] >= ov[entry_i] * (1 + sl):
            pos = 0
        if i + 1 >= m:
            continue
        if pos == 0:
            if gold[i]:
                le[i], pos, entry_i = True, 1, i + 1
            elif death[i]:
                se[i], pos, entry_i = True, -1, i + 1
        elif pos == 1 and death[i]:
            lx[i], pos = True, 0
        elif pos == -1 and gold[i]:
            sx[i], pos = True, 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
