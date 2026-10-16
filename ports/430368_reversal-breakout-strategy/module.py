"""Bollinger / stochastic scalp, broker days: the close crossing back above the lower band (20, 2) with stochastic K
crossing up through 20 goes long, the mirror at the upper band and 80 goes short; as written only the short carries the
tiny tick bracket (3-tick stop, 50-tick target, as ATR fractions); a long leaves only by a short signal.
Port of FMZ strategy #430368 "Reversal Breakout Strategy" (Bollinger Bands & Stochastic Scalping Strategy).

FMZ source id: 430368

Source
    https://www.fmz.com/strategy/430368 (PineScript v4, FMZ last modified 2023-10-27 16:14:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 130-175), BB 20 / 2, stochastic 14 / 5 / 3, target 50 ticks, stop 3 ticks from the current close
    crossover(close, lowerBB) and crossover(k, 20) -> entry long; crossunder(close, upperBB) and crossunder(k, 80) -> entry short
    every bar: exit("Take Profit/Stop Loss", from_entry = "Long", profit = 50, stop = close - 3 ticks)
               exit("Take Profit/Stop Loss", from_entry = "Short", profit = 50, stop = close + 3 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits share one id and are re-issued every bar, the short's last: the order is re-bound to
      the short entry on every bar, so a long has no exit order (it leaves only by reversal) and a short
      has the bracket. Ported as written, stated.
    * Criterion 2: 3 and 50 ticks (0.3 and 5 USD at the header market's 0.1 tick on daily BTC) become
      sl_atr / tp_atr x Wilder ATR(14) of the signal bar (0.0003 and 0.005 ATR by default), as fractions
      of its close.
    * The stop is re-issued every bar from the CURRENT close (a moving level): rule 2, mark
      trailing_stop_pending; the port fixes it at the fill. The target (ticks from the entry) is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the shared-id exit read as written, the moving stop fixed at the fill.
    2 generic: ADAPT, tick stop / target -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430368_bb_stoch_scalp_tick_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "sl_atr": [0.0003, 0.05],
    "tp_atr": [0.005, 0.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "stoch_len": 14, "smooth_k": 5, "smooth_d": 3, "sl_atr": 0.0003,
                  "tp_atr": 0.005}


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


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up_bb, lo_bb = basis + p["mult"] * sd, basis - p["mult"] * sd
    s = int(p["stoch_len"])
    ll, hh = lo.rolling(s).min(), h.rolling(s).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    long_e = (c > lo_bb) & (c.shift(1) <= lo_bb.shift(1)) & (k > 20) & (k.shift(1) <= 20)
    short_e = (c < up_bb) & (c.shift(1) >= up_bb.shift(1)) & (k < 80) & (k.shift(1) >= 80)
    return long_e.astype(bool), short_e.astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, short_e = _signals(bars_df, p)
    a = _atr(bars_df, ATR_LEN) / bars_df["close"]
    idx = bars_df.index
    sl = pd.Series(np.where(short_e, a * p["sl_atr"], np.nan), index=idx)
    tp = pd.Series(np.where(short_e, a * p["tp_atr"], np.nan), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
