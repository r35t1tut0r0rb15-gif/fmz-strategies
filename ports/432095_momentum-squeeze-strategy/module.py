"""LazyBear's squeeze momentum line (linear regression 20 of the close against the channel / SMA midline) crossing above 0 with a volume money-flow ratio (58 bars) above 50 goes long, crossing under 0 with it under 50 goes short, each with a 50 % stop and a 50 % target of the signal close; broker days, reversing.
Port of FMZ strategy #432095 "Momentum Squeeze Strategy" (Crypto Squeeze Strategy (Bunghole)).

FMZ source id: 432095

Source
    https://www.fmz.com/strategy/432095 (PineScript v4, FMZ last modified 2023-11-14 14:04:24).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 174-244), momentum linreg 20; MFI sums 58; long and short on; SL 50 %, TP 50 % (of the close, in ticks); window 1804 .. 2077
    BlueWave = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0);  mfi = (mf - 50) x 3
    buy = crossover(BlueWave, 0) and mfi > 0 -> entry Long, exit(loss = close x 50 % / mintick, profit = close x 50 % / mintick);  sell mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The money-flow function's two "if" lines are discarded values (a Pine function returns its last
      expression), so mf is the formula only; mfi > 0 is mf > 50. The exits are sent only on the signal
      bar, with distances of 50 % of that bar's close in ticks from the entry price: ported as fractions of
      the fill, close[signal] x 0.5 / open[fill]. The strategy.close calls sit inside the opposite signal's
      block and can never act (a bar cannot cross both ways); a position ends at its stop, its target or the
      opposite entry. The author's 1804 .. 2077 window is dropped. REVERSAL INTENDED. 100 % of equity is
      sizing. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at the signal close as fractions of the fill.
    2 generic: PASS, squeeze momentum zero crossings with a money-flow filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 100000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the money-flow ratio (volume x hlc3 sums over 58 bars); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 1804 .. 2077 window dropped).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432095_squeeze_momentum_zero_cross_mfi58_pct_bracket_reversal"
FAMILY = "squeeze_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mom_len": [20, 14],
    "mfi_len": [58, 30],
}
DEFAULT_PARAMS = {"mom_len": 20, "mfi_len": 58, "sl": 0.5, "tp": 0.5}


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["mom_len"])
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    bw = _linreg(c - mid, n)
    k = int(p["mfi_len"])
    src = (h + lo + c) / 3
    ch = src.diff()
    upper = (v * src.where(~(ch <= 0), 0.0)).rolling(k).sum()
    lower = (v * src.where(~(ch >= 0), 0.0)).rolling(k).sum()
    mf = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))      # the formula only, as the source returns
    mfi = (mf - 50) * 3
    bp = bw.shift(1)
    buy = (bw > 0) & (bp <= 0) & (mfi > 0)
    sell = (bw < 0) & (bp >= 0) & (mfi < 0)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.fillna(False).astype(bool), false, sell.fillna(False).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    sl_f, tp_f = float(p["sl"]) * k, float(p["tp"]) * k
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
