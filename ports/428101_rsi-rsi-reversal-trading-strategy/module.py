"""RSI of the open, broker days, AS WRITTEN: RSI 14 of the open crossing above 44 goes long (from flat,
or when the close is below the open short's entry price); crossing below 67 goes short (from flat, or
above the open long's entry). Extra entries: RSI under 15 / 20 goes long and RSI over 80 / 85 goes
short, both only when the close is below the current entry price.
Port of FMZ strategy #428101 "RSI Reversal Trading Strategy" (RSI Strategy Professional).

FMZ source id: 428101

Source
    https://www.fmz.com/strategy/428101 (PineScript v4, FMZ last modified 2023-09-28 16:09:39).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 158-241), RSI 14 of open, 44 / 67, n = 0.0577 price units
    buy = crossover(rsi, 44) and (close < avg_price - n or no open trade) -> entry long; n += 1000
    sell = crossunder(rsi, 67) and (close > avg_price + n or no open trade) -> entry short; n += 1000
    rsi < 15 or < 20, and close < avg_price - n -> entry long
    rsi > 85 or > 80, and close < avg_price - n -> entry short   (same price test as the longs)
    take-profit / stop / RSI exits: all off by default

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN, including the short extras testing close < avg price. n is not var: 0.0577 each
      bar, plus 1000 after a signal on that bar (so the extras cannot fire on a signal bar).
    * Criterion 2: n is in price units (0.0577: nothing on BTC); ported as the fraction `n_frac` of
      the entry price, default 0. The entry (average) price is the fill (next open); with pyramiding
      1 there is one trade at most, so "opentrades != 5" is always true.
    * The exits are off by default. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit offset -> fraction of the entry price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin / leverage and the off exits stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428101_rsi_open_reversal_extras"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "over_sold": [44, 30],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 44, "over_bought": 67, "n_frac": 0.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    d = o.diff()
    n = int(p["length"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    r = rsi.to_numpy()
    xo = ((rsi > p["over_sold"]) & (rsi.shift(1) <= p["over_sold"])).to_numpy()
    xu = ((rsi < p["over_bought"]) & (rsi.shift(1) >= p["over_bought"])).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    nf = float(p["n_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, entry_i = 0, -1
    for i in range(m):
        if np.isnan(r[i]):
            tgt[i] = pos
            continue
        held = pos != 0 and i >= entry_i
        avg = ov[entry_i] if held else np.nan
        flat = not held
        new = pos
        n_off = avg * nf if held else np.nan
        signal = False
        if xo[i] and (flat or cv[i] < avg - n_off):
            new, signal = 1, True
        if xu[i] and (flat or cv[i] > avg + n_off):
            new, signal = -1, True
        n_cur = n_off + (1000.0 if signal else 0.0)     # n += 1000 after a signal (price units, as written)
        if held and cv[i] < avg - n_cur:
            if r[i] < 15 or r[i] < 20:
                new = 1
            if r[i] > 85 or r[i] > 80:
                new = -1
        if new != pos:
            entry_i = i + 1
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
