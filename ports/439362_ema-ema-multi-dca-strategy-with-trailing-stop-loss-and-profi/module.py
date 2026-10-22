"""Closes within 1 % of an EMA, long only, broker days: a close within 1 % of any of the EMA 5 / 10 / 20 / 50 / 100 / 200 goes long; an ATR(20) above a threshold closes, unless an EMA test reopens the long on
the same bar.
Port of FMZ strategy #439362 "基于动态止损和目标获利的EMA多次成本加权平均成本策略EMA-Multi-DCA-Strategy-with-Trailing-Stop-Loss-and-Profit-Target" (EMA DCA Strategy with Trailing Stop and Profit Target).

FMZ source id: 439362

Source
    https://www.fmz.com/strategy/439362 (PineScript v4, FMZ last modified 2024-01-19 15:16:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-197), investment 6 per buy; ATR sell threshold 10 (price units); buy limit 3000 per EMA; trailing 1 %, target 3 % (exits name an unused id)
    if atr(20) > 10: close_all;  for each EMA: if close within 1 % of it and that EMA's count < 3000: entry "Buy at EMAn" (count + 1)
    exit("TrailingStop", from_entry = "Buy at EMA", ...);  exit("ProfitTarget", from_entry = "Buy at EMA", ...)  -- no entry has that id

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the ATR threshold of 10 price units becomes a fraction of the close, atr(20) / close >
      atr_frac; 0.00024 reads it on BTC near 42000 (always true there), 0.03 a level that bites. The
      close_all is written before the entries: a long closed by it is reopened at once when an EMA test
      holds on the bar, so it stays long; otherwise the bar ends flat. One position is held (pyramiding
      1); each EMA's count rises on every bar its test holds and stops it after 3000 such bars, as
      written. The two exits name the entry id "Buy at EMA", which no entry uses: never sent. Long only.
      The per-buy amount is sizing. Daily bars are broker days, stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit ATR threshold -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the per-buy amount stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439362_ema_band_touch_atr_close_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_frac": [0.00024, 0.03],
    "band": [0.01, 0.005],
}
DEFAULT_PARAMS = {"atr_frac": 0.00024, "band": 0.01, "atr_len": 20, "buy_limit": 3000}

EMAS = (5, 10, 20, 50, 100, 200)


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    b = float(p["band"])
    buy = pd.Series(False, index=c.index)
    for n in EMAS:
        e = c.ewm(span=n, adjust=False).mean()
        within = (c >= e * (1 - b)) & (c <= e * (1 + b))
        buy |= within & (within.cumsum() <= int(p["buy_limit"]))
    buy = buy.to_numpy()
    xc = (_atr(bars_df, p["atr_len"]) / c > float(p["atr_frac"])).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i]:
            if pos == 0:
                le[i], pos = True, 1
        elif pos == 1 and xc[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
