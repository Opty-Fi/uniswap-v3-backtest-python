from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd

from cachier import cachier


@cachier()
def graph(Adress, fromdate, tilldate=int(datetime.utcnow().timestamp())):
    client = Client(
        transport=RequestsHTTPTransport(
            url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
            verify=True,
            retries=5,
        )
    )

    query = gql('''
    query ($fromdate: Int!, $tilldate: Int!) {
        poolHourDatas(where:{pool:"'''+str(Adress)+'''",periodStartUnix_gt:$fromdate,periodStartUnix_lt:$tilldate},orderBy:periodStartUnix,orderDirection:desc,first:1000) {
            periodStartUnix
            liquidity
            high
            low
            pool {
                totalValueLockedUSD
                totalValueLockedToken1
                totalValueLockedToken0
                token0 { decimals }
                token1 { decimals }
                }
            close
            feeGrowthGlobal0X128
            feeGrowthGlobal1X128
        }
    }
    ''')

    out = None
    while fromdate < tilldate:
        params = {
            "fromdate": fromdate,
            "tilldate": tilldate,
        }

        tilldate -= 1000 * 3600

        response = client.execute(query, variable_values=params)
        dpd = pd.json_normalize(response['poolHourDatas'])
        dpd = dpd.astype(float).astype({"periodStartUnix": int})

        if out is None:
            out = dpd
        else:
            out = pd.concat([dpd, out], ignore_index=True)

    return out
