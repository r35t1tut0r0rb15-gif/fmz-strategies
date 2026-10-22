"""TD Sequential 9-count setups against the SMA 10 with an SMA 200 trend filter, broker days: a completed buy setup (9 closes in a row not above the close 4 bars back) with the close under the SMA 10
and above the SMA 200 goes long, closed when the close is back above the SMA 10; the sell setup mirrors it under the SMA 200; a 1 % target and 1 % stop; reversing.
Port of FMZ strategy #441163 "量化交易双向S-R策略TD-Sequential-Dual-Direction-S-R-Trading-Strategy" (GMS: TD Sequential Strategy).

FMZ source id: 441163

Source
    https://www.fmz.com/strategy/441163 (PineScript v4, FMZ last modified 2024-02-06 12:13:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-731), defaults: both sides; price flips 9 / 9; exit MAs SMA 10 / 10; long trend Above, short trend Below; trend SMA 200; profit target 1 % on, stop loss -1 % on
    every bar: strategy.exit(profit = close 1 % / mintick, loss = close 1 % / mintick)
    priceflip1 = barssince(close > close[4]);  buysetup = close < close[4] and priceflip1;  barssince(priceflip1 != 9) is true only when priceflip1 == 9 (the sell side mirrors it)
    (the active default block, lines 229-230 and 246-247) buysetup and barssince(priceflip1 != 9) and close < sma10 and close > sma200 -> entry LONG;  close > sma10 -> close LONG
    sellsetup and barssince(priceflip != 9) and close > sma10 and close < sma200 -> entry SHORT;  close < sma10 -> close SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the block selected by the default inputs runs (SMA exits, SMA trend; the VWMA blocks are not
      used). barssince(priceflip1 != 9) is 0 (false) unless the count is exactly 9, so the setup completes
      on the ninth bar. The bracket is in ticks, re-sized every bar from the close: the port reads it as
      fixed fractions of the entry (as #437751), target 0.01 and stop 0.01. A close acts only on the held
      position; a close written after a reversing entry leaves the reversal standing (as #438020).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket from the close -> fixed fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441163_td_sequential_9_sma10_revert_sma200_bracket"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "price_flip": [9, 13],
    "exit_len": [10, 20],
}
DEFAULT_PARAMS = {"price_flip": 9, "exit_len": 10, "trend_len": 200, "tp": 0.01, "sl": 0.01}


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


def _count_since(cond):
    """Pine barssince(cond): bars since cond was last true (-1 before the first)."""
    out = np.full(len(cond), -1)
    k = -1
    for i, f in enumerate(cond):
        if f:
            k = 0
        elif k >= 0:
            k += 1
        out[i] = k
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    c4 = c.shift(4)
    fl = int(p["price_flip"])
    n_up = _count_since((c > c4).to_numpy())
    n_dn = _count_since((c < c4).to_numpy())
    buy = (c < c4).to_numpy() & (n_up == fl)
    sell = (c > c4).to_numpy() & (n_dn == fl)
    sx_ = c.rolling(int(p["exit_len"])).mean()
    st = c.rolling(int(p["trend_len"])).mean()
    el = buy & ((c < sx_) & (c > st)).to_numpy()
    xl = (c > sx_).to_numpy()
    es = sell & ((c > sx_) & (c < st)).to_numpy()
    xs = (c < sx_).to_numpy()
    s_, t_ = float(p["sl"]), float(p["tp"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        held = pos
        if el[i] and pos != 1 and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        elif xl[i] and held == 1 and pos == 1 and i >= entry_i:
            lx[i], pos = True, 0
        if es[i] and pos != -1 and i + 1 < m:
            lx[i] = False
            se[i], pos, entry_i = True, -1, i + 1
        elif xs[i] and held == -1 and pos == -1 and i >= entry_i:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
