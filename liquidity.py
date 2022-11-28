import numpy as np


def get_amount0(sqrtA, sqrtB, liquidity, decimals):
    if (sqrtA > sqrtB):
        (sqrtA, sqrtB) = (sqrtB, sqrtA)

    return ((liquidity*2**96*(sqrtB-sqrtA)/sqrtB/sqrtA)/10**decimals)


def get_amount1(sqrtA, sqrtB, liquidity, decimals):
    if (sqrtA > sqrtB):
        (sqrtA, sqrtB) = (sqrtB, sqrtA)

    return liquidity*(sqrtB-sqrtA)/2**96/10**decimals


def get_amounts(asqrt, asqrtA, asqrtB, liquidity, decimal0, decimal1):
    sqrt = (np.sqrt(asqrt*10**(decimal1-decimal0)))*(2**96)
    sqrtA = np.sqrt(asqrtA*10**(decimal1-decimal0))*(2**96)
    sqrtB = np.sqrt(asqrtB*10**(decimal1-decimal0))*(2**96)

    if (sqrtA > sqrtB):
        (sqrtA, sqrtB) = (sqrtB, sqrtA)

    if sqrt <= sqrtA:
        amount0 = get_amount0(sqrtA, sqrtB, liquidity, decimal0)
        return amount0, 0
    elif sqrt < sqrtB and sqrt > sqrtA:
        amount0 = get_amount0(sqrt, sqrtB, liquidity, decimal0)
        amount1 = get_amount1(sqrtA, sqrt, liquidity, decimal1)
        return amount0, amount1
    else:
        amount1 = get_amount1(sqrtA, sqrtB, liquidity, decimal1)
        return 0, amount1


def get_liquidity0(sqrtA, sqrtB, amount0, decimals):
    if (sqrtA > sqrtB):
        (sqrtA, sqrtB) = (sqrtB, sqrtA)

    return amount0/((2**96*(sqrtB-sqrtA)/sqrtB/sqrtA)/10**decimals)


def get_liquidity1(sqrtA, sqrtB, amount1, decimals):
    if (sqrtA > sqrtB):
        (sqrtA, sqrtB) = (sqrtB, sqrtA)

    return amount1/((sqrtB-sqrtA)/2**96/10**decimals)


def get_liquidity(asqrt, asqrtA, asqrtB, amount0, amount1, decimal0, decimal1):
    sqrt = (np.sqrt(asqrt*10**(decimal1-decimal0)))*(2**96)
    sqrtA = np.sqrt(asqrtA*10**(decimal1-decimal0))*(2**96)
    sqrtB = np.sqrt(asqrtB*10**(decimal1-decimal0))*(2**96)

    if (sqrtA > sqrtB):
        (sqrtA, sqrtB) = (sqrtB, sqrtA)

    if sqrt <= sqrtA:
        return get_liquidity0(sqrtA, sqrtB, amount0, decimal0)
    elif sqrt < sqrtB and sqrt > sqrtA:
        liquidity0 = get_liquidity0(sqrt, sqrtB, amount0, decimal0)
        liquidity1 = get_liquidity1(sqrtA, sqrt, amount1, decimal1)
        liquidity = liquidity0 if liquidity0 < liquidity1 else liquidity1
        return liquidity
    else:
        return get_liquidity1(sqrtA, sqrtB, amount1, decimal1)
