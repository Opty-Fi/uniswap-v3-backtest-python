import numpy as np
import liquidity
import GraphBacktest
import charts


Adress = "0x6c6bc977e13df9b0de53b251522280bb72383700"  # DAI/USDC 0.05%
# Adress = "0x3416cf6c708da44db2624d63ea0aaef7113527c6"  # USDC/USDT 0.01%
# Adress = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"  # ETH USDC Ethereum
startfrom = 1_660_000_000

dpd = GraphBacktest.graph(Adress, startfrom)

print(dpd)


decimal0 = dpd.iloc[0]['pool.token0.decimals']
decimal1 = dpd.iloc[0]['pool.token1.decimals']
decimal = decimal1-decimal0
dpd['fg0'] = ((dpd['feeGrowthGlobal0X128'])/(2**128))/(10**decimal0)
dpd['fg1'] = ((dpd['feeGrowthGlobal1X128'])/(2**128))/(10**decimal1)

mini = 0.995
maxi = 1.005
target = 10000
base = 0


# Calculate F0G and F1G (fee earned by an unbounded unit of liquidity in one period)

dpd['fg0shift'] = dpd['fg0'].shift(-1)
dpd['fg1shift'] = dpd['fg1'].shift(-1)
dpd['fee0token'] = dpd['fg0']-dpd['fg0shift']
dpd['fee1token'] = dpd['fg1']-dpd['fg1shift']

# calculate my liquidity

SMIN = np.sqrt(mini * 10 ** (decimal))
SMAX = np.sqrt(maxi * 10 ** (decimal))

if base == 0:
    sqrt0 = np.sqrt(dpd['close'].iloc[-1] * 10 ** (decimal))
    dpd['price0'] = dpd['close']
else:
    sqrt0 = np.sqrt(1/dpd['close'].iloc[-1] * 10 ** (decimal))
    dpd['price0'] = 1/dpd['close']

if sqrt0 > SMIN and sqrt0 < SMAX:
    deltaL = target / ((sqrt0 - SMIN) + (((1 / sqrt0) - (1 / SMAX))
                       * (dpd['price0'].iloc[-1] * 10 ** (decimal))))
    amount1 = deltaL * (sqrt0-SMIN)
    amount0 = deltaL * ((1/sqrt0)-(1/SMAX)) * 10 ** (decimal)
elif sqrt0 < SMIN:
    deltaL = target / (((1 / SMIN) - (1 / SMAX)) * (dpd['price0'].iloc[-1]))
    amount1 = 0
    amount0 = deltaL * ((1/SMIN) - (1/SMAX))
else:
    deltaL = target / (SMAX-SMIN)
    amount1 = deltaL * (SMAX-SMIN)
    amount0 = 0


print("Amounts:", amount0, amount1)

# print(dpd['price0'].iloc[-1],mini,maxi)
# print((dpd['price0'].iloc[-1],mini,maxi,amount0,amount1,decimal0,decimal1))
myliquidity = liquidity.get_liquidity(
    dpd['price0'].iloc[-1], mini, maxi, amount0, amount1, decimal0, decimal1)

print("OK myliquidity", myliquidity)

# Calculate ActiveLiq

dpd['ActiveLiq'] = 0
dpd['amount0'] = 0
dpd['amount1'] = 0
dpd['amount0unb'] = 0
dpd['amount1unb'] = 0

if base == 0:
    for i, row in dpd.iterrows():
        if dpd['high'].iloc[i] > mini and dpd['low'].iloc[i] < maxi:
            dpd.iloc[i, dpd.columns.get_loc('ActiveLiq')] = (min(maxi, dpd['high'].iloc[i]) - max(
                dpd['low'].iloc[i], mini)) / (dpd['high'].iloc[i]-dpd['low'].iloc[i]) * 100
        else:
            dpd.iloc[i, dpd.columns.get_loc('ActiveLiq')] = 0

        amounts = liquidity.get_amounts(
            dpd['price0'].iloc[i], mini, maxi, myliquidity, decimal0, decimal1)
        dpd.iloc[i, dpd.columns.get_loc('amount0')] = amounts[1]
        dpd.iloc[i, dpd.columns.get_loc('amount1')] = amounts[0]

        amountsunb = liquidity.get_amounts(
            (dpd['price0'].iloc[i]), 1.0001**(-887220), 1.0001**887220, 1, decimal0, decimal1)
        dpd.iloc[i, dpd.columns.get_loc('amount0unb')] = amountsunb[1]
        dpd.iloc[i, dpd.columns.get_loc('amount1unb')] = amountsunb[0]

else:
    for i, row in dpd.iterrows():
        if (1 / dpd['low'].iloc[i]) > mini and (1 / dpd['high'].iloc[i]) < maxi:
            dpd.iloc[i, dpd.columns.get_loc('ActiveLiq')] = (min(maxi, 1 / dpd['low'].iloc[i]) - max(
                1 / dpd['high'].iloc[i], mini)) / ((1 / dpd['low'].iloc[i]) - (1 / dpd['high'].iloc[i])) * 100
        else:
            dpd.iloc[i, dpd.columns.get_loc('ActiveLiq')] = 0

        amounts = liquidity.get_amounts(
            (dpd['price0'].iloc[i]*10**(decimal)), mini, maxi, myliquidity, decimal0, decimal1)
        dpd.iloc[i, dpd.columns.get_loc('amount0')] = amounts[0]
        dpd.iloc[i, dpd.columns.get_loc('amount1')] = amounts[1]

        amountsunb = liquidity.get_amounts(
            (dpd['price0'].iloc[i]), 1.0001**(-887220), 1.0001**887220, 1, decimal0, decimal1)
        dpd.iloc[i, dpd.columns.get_loc('amount0unb')] = amountsunb[0]
        dpd.iloc[i, dpd.columns.get_loc('amount1unb')] = amountsunb[1]


# Final fee calculation

dpd['myfee0'] = dpd['fee0token'] * myliquidity * dpd['ActiveLiq'] / 100
dpd['myfee1'] = dpd['fee1token'] * myliquidity * dpd['ActiveLiq'] / 100

# print(dpd)

a = charts.chart1(dpd, base, myliquidity)
