"""Buy-low / sell-high bands, daily bars, long only: the close 2 % under its 10-bar highest close goes long; the close 2 % over its 10-bar lowest close closes (both often hold together).
Port of FMZ strategy #443124 "The Momentum Breakout Strategy" (Achat/Vente (Strategie d'achat bas / vendre haut)).

FMZ source id: 443124

Source
    https://www.fmz.com/strategy/443124 (PineScript v5, FMZ last modified 2024-02-29 14:04:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-190), buy threshold 0.02, sell threshold 0.02; 10-bar high / low of the close; fee rate and balances (display)
    close < highest(close, 10) (1 - 0.02) -> entry Achat;  close > lowest(close, 10) (1 + 0.02) -> close Achat

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests often hold on one bar: the entry is sent first and the close acts only on a held
      long, so from flat the bar enters and a later bar with the close test true exits, as written.
      The balance and fee arithmetic only plots. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, distance from the 10-bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443124_buy_low_sell_high_10bar_bands_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_threshold": [0.02, 0.05],
    "sell_threshold": [0.02, 0.05],
}
DEFAULT_PARAMS = {"buy_threshold": 0.02, "sell_threshold": 0.02, "window": 10}


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
    w = int(p["window"])
    go = (c < c.rolling(w).max() * (1 - float(p["buy_threshold"]))).to_numpy()
    out = (c > c.rolling(w).min() * (1 + float(p["sell_threshold"]))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
