"""One-minute bars, long only: a stochastic-RSI (14 / 14 / 3 / 2) K-D cross up under 34 with the MACD 12 / 26 / 9 under its signal and the MFI 14 under 23 goes long; a K-D cross down above 80 with the MACD above its signal and the MFI over 80 closes (short entries are disallowed, so the short signal is an exit).
Port of FMZ strategy #434555 "Johns Bitcoin Intraday Trading Strategy Based on Multiple Indicators" (John Day Stop Loss).

FMZ source id: 434555

Source
    https://www.fmz.com/strategy/434555 (PineScript v5, FMZ last modified 2023-12-07 15:23:44).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 148-245), stochastic RSI 14 / 14, K 3, D 2, 34 / 80; MACD 12 / 26 / 9 (EMA); MFI 14, 23 / 80; RSI filters true; stop 2.1 % (see interp); window 2021 .. 2025
    strategy.risk.allow_entry_in(long);  buy = crossover(k, d) and k < 34 and macd < signal and hist < 0 and mfi < 23 -> entry BUY, exit(stop = avg x 0.979)
    sell = crossunder(k, d) and k > 80 and macd > signal and hist > 0 and mfi > 80 -> entry SELL (turned into a close of the long by allow_entry_in)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.risk.allow_entry_in(strategy.direction.long) makes the SELL entry an exit of the long. The
      2.1 % stop is sent on the BUY signal bar with stop = position_avg_price x 0.979, which is na while
      flat, so no stop order exists on a fresh entry; it only becomes real if the BUY set repeats while
      long (pyramiding 1). That path-dependent stop is not ported (weird case): the port has no stop.
      buy_rsi / sell_rsi are true. The 2021 .. 2025 window is dropped. Long only. 10000 cash per trade is
      sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic-RSI, MACD and MFI oversold entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10000 cash per trade, capital 10000, pyramiding 1, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in ta.mfi(hlc3, 14) (entry under 23, exit over 80); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2021 .. 2025 window dropped).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434555_stochrsi_macd_mfi_oversold_1m_long"
FAMILY = "stochastic_rsi"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mfi_buy": [23, 30],
    "os_level": [34.0, 20.0],
}
DEFAULT_PARAMS = {"mfi_buy": 23, "mfi_sell": 80, "os_level": 34.0, "ob_level": 80.0, "smooth_k": 3, "smooth_d": 2,
                  "rsi_len": 14, "stoch_len": 14}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _mfi(src, vol, n):
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    r = _rsi(c, int(p["rsi_len"]))
    ns = int(p["stoch_len"])
    rl, rh = r.rolling(ns).min(), r.rolling(ns).max()
    k = (100 * (r - rl) / (rh - rl).where(rh != rl)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    co = (k > d) & (k.shift(1) <= d.shift(1))
    cu = (k < d) & (k.shift(1) >= d.shift(1))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hist = macd - sig
    mf = _mfi((h + lo + c) / 3, v, 14)
    defined = k.notna() & d.notna()
    buy = (defined & co & (k < float(p["os_level"])) & (macd < sig) & (hist < 0) & (mf < float(p["mfi_buy"]))).to_numpy()
    sell = (defined & cu & (k > float(p["ob_level"])) & (macd > sig) & (hist > 0) & (mf > float(p["mfi_sell"]))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            le[i], pos = True, 1
        elif pos == 1 and sell[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
