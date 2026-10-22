"""RSI 14 bullish divergences with a Hull-smoothed RSI, 1-minute bars, long only: the RSI under 30 and its Hull 10 under 35 and falling three bars, the price under its value at the 25-bar RSI low while
the RSI is above that low, go long; a 3 % target and 1.75 % stop of the fill; the RSI over 65 closes.
Port of FMZ strategy #443241 "RSI与平滑RSI策略多头分型RSI-and-smoothed-RSI-bullish-divergence-strategy" (RSI and Smoothed RSI Bull Div Strategy [BigBitsIO]).

FMZ source id: 443241

Source
    https://www.fmz.com/strategy/443241 (PineScript v4, FMZ last modified 2024-03-01 12:11:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-189), RSI 14; Hull 10 of the RSI; divergence lookback 25 (low under 25); take profit 3 %, stop 1.75 % (as percent / mintick ticks); buy-below 0 %; 100 % of equity, commission 0.1
    SRSI = wma(2 wma(RSI, 5) - wma(RSI, 10), 3);  down-length counts falling SRSI bars;  BuyBelowTarget = close at the 25-bar RSI low
    IsABuy = RSI < 30 and SRSI < 35 and lowest(SRSI, 25) < 25 and close < BuyBelowTarget and down-length >= 3 and RSI > lowest(RSI, 25) -> entry, exit(profit = 3 % / mintick, loss = 1.75 % / mintick)
    IsASell = RSI > 65 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a percentage of the signal close over the tick, a tick distance from the fill:
      fixed fractions 0.03 / 0.0175 of the fill (#437751); a new signal while long moves the script's
      levels, which the port does not follow (as #439608). lowestbars is read as the most recent lowest
      RSI in the window. Long only. Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size
      and commission are sizing and costs. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, RSI divergence with a smoothed RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_443241_rsi_hull_bull_divergence_pct_bracket_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_curve": [14, 7],
    "div_lookback": [25, 50],
}
DEFAULT_PARAMS = {"rsi_curve": 14, "div_lookback": 25, "srsi_curve": 10, "tp_pct": 0.03, "sl_pct": 0.0175,
                  "rsi_below": 30, "srsi_below": 35, "low_below": 25, "sell_above": 65, "min_down": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_curve"]))
    sc = int(p["srsi_curve"])
    srsi = _wma(2 * _wma(r, sc // 2) - _wma(r, sc), int(np.floor(np.sqrt(sc) + 0.5)))
    sv = srsi.to_numpy()
    m = len(c)
    down = np.zeros(m)
    for i in range(1, m):
        down[i] = down[i - 1] + 1 if sv[i] < sv[i - 1] else 0
    lb = int(p["div_lookback"])
    rv, cv = r.to_numpy(), c.to_numpy(dtype=float)
    target = np.full(m, np.nan)
    for i in range(lb - 1, m):
        w = rv[i - lb + 1:i + 1]
        if np.isnan(w).any():
            continue
        k = lb - 1 - int(np.argmin(w[::-1]))          # the most recent lowest RSI in the window
        target[i] = cv[i - lb + 1 + k]
    rmin = r.rolling(lb).min()
    with np.errstate(invalid="ignore"):
        buy = ((r < float(p["rsi_below"])) & (srsi < float(p["srsi_below"]))
               & (srsi.rolling(lb).min() < float(p["low_below"])) & (c < target)
               & (down >= int(p["min_down"])) & (r > rmin)).to_numpy()
    sell = (r > float(p["sell_above"])).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - s_) or hv[i] >= ov[entry_i] * (1 + t_)):
            pos = 0
        if pos == 0 and buy[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        elif pos == 1 and i >= entry_i and sell[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
