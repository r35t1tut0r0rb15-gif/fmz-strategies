"""RSI 8 extremes with tick brackets and bar-count exits, broker days: the RSI 8 crossing under 23 goes long and crossing
over 75 goes short; a long closes when the RSI crosses over 78 or 16 bars after its signal, a short when the RSI
crosses under 35 or 26 bars after its signal. Each side has its own tick target / stop (406 / 189 long, 370 / 152
short), which become ATR multiples.
Port of FMZ strategy #433128 "RSI跳空反转策略RSI-Gap-Reversal-Strategy" (GBP combine).

FMZ source id: 433128

Source
    https://www.fmz.com/strategy/433128 (PineScript v3, FMZ last modified 2023-11-24 16:01:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-185), RSI 8, oversold 23, overbought 75, exit levels 35 / 78; bars 16 / 26; ticks long 406 / 189, short 370 / 152
    crossunder(rsi, 23) -> entry long, exit(profit = 406, loss = 189);  crossover(rsi, 78) or barssince(long signal) > 16 -> close long
    crossover(rsi, 75) -> entry short, exit(profit = 370, loss = 152);  crossunder(rsi, 35) or barssince(short signal) > 26 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the brackets are in ticks. On the header's BTC_USDT (mintick 0.1) 406 ticks is 40.6
      USD, about 0.04 ATR of daily BTC; the script's "GBP" reading (a 0.00001 tick) gives about 0.4 ATR
      of daily GBPUSD. Each distance becomes ticks / 100 x atr_per_100_ticks x Wilder ATR 14 of the
      signal bar, as a fraction of its close (shifted one bar, re-based on the fill); the grid holds
      both readings. The side of the target and stop is taken from the signal (read on the fill bar).
    * The bar-count exit closes a position whose last same-side signal is more than 16 (26) bars old.
      An exit on the bar of an opposite entry is left to the entry (strategy.entry reverses):
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; stops on daily bars: mark
      coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; bar-count exits as signals.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick brackets quoted in original_sizing.txt.
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

NAME = "fmz_433128_rsi8_extremes_tick_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_per_100_ticks": [0.01, 0.1],
    "length": [8, 14],
}
DEFAULT_PARAMS = {"length": 8, "over_sold": 23, "over_bought": 75, "over_sold_p": 35, "over_bought_p": 78,
                  "profit_l": 406, "loss_l": 189, "profit_s": 370, "loss_s": 152, "bars_l": 16, "bars_s": 26,
                  "atr_per_100_ticks": 0.01, "atr_len": 14}


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


def _barssince(v):
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ch = c.diff()
    n = int(p["length"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    r1 = r.shift(1)
    le = ((r < p["over_sold"]) & (r1 >= p["over_sold"])).to_numpy()
    se = ((r > p["over_bought"]) & (r1 <= p["over_bought"])).to_numpy()
    with np.errstate(invalid="ignore"):
        lx = ((r > p["over_bought_p"]) & (r1 <= p["over_bought_p"])).to_numpy() | (_barssince(le) > int(p["bars_l"]))
        sx = ((r < p["over_sold_p"]) & (r1 >= p["over_sold_p"])).to_numpy() | (_barssince(se) > int(p["bars_s"]))
    lx, sx = lx & ~se, sx & ~le
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["atr_per_100_ticks"]) / 100
    return le, lx, se, sx, af


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _signals(bars_df, p)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _, _, af = _signals(bars_df, p)
    tp = pd.Series(np.where(le, float(p["profit_l"]), float(p["profit_s"])), index=bars_df.index) * af
    sl = pd.Series(np.where(le, float(p["loss_l"]), float(p["loss_s"])), index=bars_df.index) * af
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
