"""SuperTrend (10, 3) direction changes, broker days: a turn up goes long, a turn down goes short; reversing. Each trade has a stop beyond the signal bar's low (high) and a target beyond its high (low) by fixed
price amounts, re-expressed as fractions of the close; a close 9 % under the previous close closes a long, a close 1 % over it closes a short.
Port of FMZ strategy #438054 "Supertrend Moving Stop Loss Take Profit Strategy" (ST Michael Moving TP).

FMZ source id: 438054

Source
    https://www.fmz.com/strategy/438054 (PineScript v5, FMZ last modified 2024-01-08 16:24:03).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 90-130), stop amount 1500, profit amount 15000 (price units); long trail 0.91, short trail 1.01; SuperTrend ATR 10, factor 3; 15 % of equity
    change(direction) < 0 -> entry Long3;  > 0 -> entry Short3;  stop = valuewhen(signal, low - 1500), limit = valuewhen(signal, high + 15000) (shorts mirror)
    long and close < close[1] x 0.91 -> close Long3;  short and close > close[1] x 1.01 -> close Short3

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop and profit amounts are price units; the port adds stop_frac (profit_frac) x
      the close to the signal bar's distance from the close to its low or high: 0.036 / 0.36 are the
      reading (1500 / 15000 on BTC near 42000 at the header's end), 0.05 a wider stop. The levels are fixed
      at the signal bar and re-based on the fill (sl_stop / tp_stop shifted one bar inside stops()); the
      exit is sent from the first bar close inside the trade, one bar after the fill: the port starts it
      at the fill. The trailing-profit closes are close tests. strategy.entry reverses: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. The 15 %
      of equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit stop and profit amounts -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_438054_supertrend_turn_price_bracket"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [0.036, 0.05],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"stop_frac": 0.036, "factor": 3.0, "profit_frac": 0.36, "atr_period": 10,
                  "long_trail": 0.91, "short_trail": 1.01}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _supertrend_dir(h, lo, c, factor, n):
    """Direction of Pine's ta.supertrend(factor, atrPeriod): -1 up, 1 down, nan before the ATR."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return pd.Series(d, index=c.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d = _supertrend_dir(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    ch = d - d.shift(1)
    return ch < 0, ch > 0


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    up, dn = _signals(bars_df, p)
    lx = c < c.shift(1) * float(p["long_trail"])
    sx = c > c.shift(1) * float(p["short_trail"])
    return up, lx & ~up & ~dn, dn, sx & ~up & ~dn


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, _ = _signals(bars_df, p)
    on_long = up.to_numpy()
    sf, pf = float(p["stop_frac"]), float(p["profit_frac"])
    sl = np.where(on_long, ((c - lo) / c).to_numpy() + sf, ((h - c) / c).to_numpy() + sf)
    tp = np.where(on_long, ((h - c) / c).to_numpy() + pf, ((c - lo) / c).to_numpy() + pf)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
