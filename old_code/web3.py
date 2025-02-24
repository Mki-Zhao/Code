from web3 import Web3

address = "0xb83353106f18068f649c36dc8917585e3249b054"

provider_rpc = {
    "development": "http://localhost:9944",
    "bsc_testnet": "https://go.getblock.io/3c397ff1fbd24b6686f6ff68b3bd1cf3"
# https://account.getblock.io/ 免费节点url
}

bsc_testnet = Web3(Web3.HTTPProvider(provider_rpc["bsc_testnet"]))  #通过HTTPProvider 链接到指定的RPC

#print(bsc_testnet.is_connected())      #返会连接是否成功，成功返回True,失败False
#print(bsc_testnet.eth.get_block_number())       #.eth对链上进行操作，返回最新的区块编号

balance_wei = bsc_testnet.eth.get_balance(bsc_testnet.to_checksum_address(address))
balance_ether = bsc_testnet.from_wei(balance_wei,"ether")
balance_wei = bsc_testnet.to_wei(balance_ether,"ether")

print(f"余额：{balance_ether}")


address = bsc_testnet.to_checksum_address(address)
count = bsc_testnet.eth.get_transaction_count(address)
print(f"交易次数：{count}")

gas_price = bsc_testnet.eth.gas_price
gas_estimate = bsc_testnet.eth.estimate_gas(
    {
        'to' : address_to,
        'from': address_from,
        'value' : bsc_testnet.to_wei(max_balance,'wei')
    }
)

#构建一笔交易所需要的数据
tx = {
    'nonce' : nonce,
    'to' : address_to,
    'value': max_balance,
    'gas': 21000,
    'gasPrice' : gas_price,
    'chainId' : bsc_testnet.eth.chain_id
}















