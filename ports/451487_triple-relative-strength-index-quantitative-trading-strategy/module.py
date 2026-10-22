"""RSI 5 dips in an uptrend, daily bars, long only: an RSI under 35 after three straight falls from under 60, with the close over the SMA 200, buys from flat; an RSI over 50 closes.
Port of FMZ strategy #451487 "Triple Relative Strength Index Quantitative Trading Strategy" (Triple RSI [Honestcowboy]).

FMZ source id: 451487

Source
    https://www.fmz.com/strategy/451487 (PineScript v5, FMZ last modified 2024-05-15 10:23:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-155), RSI 5 (rma; 100 when no losses, 0 when no gains); SMA 200
    rsi < 35 and rsi < rsi[1] < rsi[2] < rsi[3] and rsi[3] < 60 and close > sma200 and flat -> entry LONG;  rsi > 50 -> close LONG

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI is written out by hand with Pine's guards (no losses -> 100, no gains -> 0). Entries only
      from flat; the entry and the close cannot meet on one bar (35 against 50). Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, falling-RSI dips above the SMA 200.
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

NAME = "fmz_451487_triple_falling_rsi5_dip_above_sma200_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [5, 3],
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"rsi_len": 5, "sma_len": 200, "entry_lvl": 35.0, "start_lvl": 60.0, "exit_lvl": 50.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["rsi_len"])
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = 100 - 100 / (1 + up / dn)
    rsi = raw.mask(up == 0, 0.0).mask(dn == 0, 100.0).where(up.notna() & dn.notna())
    r1, r2, r3 = rsi.shift(1), rsi.shift(2), rsi.shift(3)
    sma = c.rolling(int(p["sma_len"])).mean()
    le = ((rsi < float(p["entry_lvl"])) & (rsi < r1) & (r1 < r2) & (r2 < r3)
          & (r3 < float(p["start_lvl"])) & (c > sma))
    lx = rsi > float(p["exit_lvl"])
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
