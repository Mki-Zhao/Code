import time
import random
import requests
import ccxt
from termcolor import cprint


def get_public_ip() -> str:
    """
    获取当前公网 IP 地址

    Returns:
        str: 公网 IP 地址或错误信息
    """
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        if response.status_code == 200:
            return response.json().get("ip", "Unknown IP")
        else:
            return "无法获取 IP"
    except Exception as e:
        return f"获取 IP 时出错: {e}"


def binance_withdraw(address: str,
                     amount_to_withdrawal: float,
                     symbol_withdraw: str,
                     network: str,
                     api_key: str,
                     api_secret: str,
                     tag=None) -> None:
    """
    通过币安进行提现

    Args:
        address (str): 提现目标钱包地址
        amount_to_withdrawal (float): 提现金额
        symbol_withdraw (str): 提现币种
        network (str): 指定提现网络
        api_key (str): API Key
        api_secret (str): Secret Key
        tag (str, optional): 其他参数，如Memo或Tag。默认为 None.
    """
    # 创建币安交易所实例，自动调整时间差
    account_binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True
        }
    })

    try:
        # 检查账户余额
        balances = account_binance.fetch_balance()
        if balances[symbol_withdraw]['free'] < amount_to_withdrawal:
            cprint(f"余额不足，无法提取 {amount_to_withdrawal} {symbol_withdraw}", "yellow")
            return

        # 手动同步时间差
        server_time = account_binance.fetch_time()  # 获取服务器时间
        local_time = account_binance.milliseconds()  # 获取本地时间
        time_difference = server_time - local_time  # 计算时间差

        # 打印时间差，供调试时查看
        print(f"Server time: {server_time}, Local time: {local_time}, Time difference: {time_difference} ms")

        # 在提币请求前手动调整时间戳，确保与服务器时间同步.这里是让本地的时间不快过服务器，把本地的时间以参数的形式发送给币安服务器
        account_binance.options['timestamp'] = account_binance.milliseconds() - 2000  # 延迟 1500 毫秒


        # 发起提现请求
        account_binance.withdraw(
            code=symbol_withdraw,
            amount=amount_to_withdrawal,
            address=address,
            tag=tag,
            params={
                "network": network,
                "name": "WalletName"
            }
        )
        cprint(f">>> 成功 | {address} | 提现金额: {amount_to_withdrawal}", "green")

    except ccxt.NetworkError as e:
        cprint(f">>> 网络错误 | {address} | 错误信息: {e}", "red")
    except ccxt.ExchangeError as e:
        cprint(f">>> 交易所错误 | {address} | 错误信息: {e}", "red")
    except Exception as e:
        cprint(f">>> 未知错误 | {address} | 错误信息: {e}", "red")


def main():
    # 获取当前公网 IP 地址
    current_ip = get_public_ip()
    cprint(f"当前公网 IP: {current_ip}", "cyan")

    # 从文件中加载钱包地址列表
    with open("../wallets.txt", "r") as f:
        wallets_list = [row.strip() for row in f if row.strip()]

    # 配置 API 相关信息与提现参数
    API_KEY = "h4u79E93GHFIYB7fR3P5bDNJZGhKTcxKMBgP1A7tNRTCDWt9nqeAwVZ39Q67LRiV"
    API_SECRET = "Q23YDTkOsEWaxapHJ06tRTqz5sozWwNcyn1XAFscP4Ns3AFeSdyTMgx7PrM0iMQf"
    symbol_withdraw = 'USDT'      # 可修改币种
    network = 'Optimism'          # 可修改提现网络
    AMOUNT_FROM = 10             # 最小提现金额
    AMOUNT_TO = 12               # 最大提现金额
    tag = None

    cprint('\a\n/// 开始提现操作...', 'red')

    for wallet in wallets_list:
        # 随机生成提现金额，并保留6位小数
        amount_to_withdrawal = round(random.uniform(AMOUNT_FROM, AMOUNT_TO), 6)
        binance_withdraw(wallet, amount_to_withdrawal, symbol_withdraw, network, API_KEY, API_SECRET, tag)
        # 随机等待15到30秒，防止触发频率限制
        time.sleep(random.randint(15, 30))


if __name__ == "__main__":
    main()

    """
    该函数用于从币安交易所账户提币。
    参数:
    - address: 提币地址，接收提币的目标地址。
    - amount_to_withdrawal: 提币的金额。
    - symbolWithdraw: 提币的币种（如BNB）。
    - network: 提币使用的网络（如BSC）。
    - API_KEY: 币安API的访问密钥。
    - API_SECRET: 币安API的密钥。

    常见网络选择
    BSC（币安智能链）
    ETH（以太坊）
    AVAXC（Avalanche C-Chain）
    MATIC（Polygon）
    ARBITRUM（Arbitrum）
    OPTIMISM（Optimism）
    TRX（TRON）
    SOL（Solana）
    APT（Aptos）

    Currency	Network
    ETH	ERC20
    TRX	TRC20
    BSC	BEP20
    BNB	BEP2
    HT	HECO
    OMNI	OMNI

    返回值:
    - 无
    """