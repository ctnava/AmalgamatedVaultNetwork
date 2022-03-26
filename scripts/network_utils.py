import os, json, time
from brownie import *
from dotenv import load_dotenv
from .contract_utils import testnet_bank, testnet_bank2
from .gas_strategy import select_strategy


def dev_check():
	if network.main.show_active() == "development":
		print("DevNet detected... funding testnet accounts\n")
		accounts[0].transfer(testnet_bank, accounts[1].balance()) 
		time.sleep(1)
		accounts[1].transfer(testnet_bank2, accounts[1].balance()) 
		time.sleep(1)
		print("Success!")

def mainnet_selector():
	load_dotenv()
	ntwrk = network.main.show_active()
	
	if ntwrk != "development":
		selection = "mainnet-m" if ntwrk[-2:] == "-m" else "mainnet"
		return selection
	else:
		moralis_key = os.getenv('MORALIS_KEY')
		selection = "mainnet-m" if moralis_key != None else "mainnet"
		return selection


def testnet_selector():
	load_dotenv()
	ntwrk = network.main.show_active()
	
	if ntwrk != "development":
		selection = "ropsten-m" if ntwrk[-2:] == "-m" else "ropsten"
		return selection
	else:
		moralis_key = os.getenv('MORALIS_KEY')
		selection = "ropsten-m" if moralis_key != None else "ropsten"
		return selection


from brownie.network.web3 import web3
def reconnect(subnet):
	previous_network = network.main.show_active()
	
	if subnet != previous_network:
		print("Switching to " + subnet + " from " + previous_network + "...")
		while not web3.isConnected():
			pass
		network.main.disconnect()
		network.main.connect(subnet)
		select_strategy()
		assert network.main.show_active() == subnet
		print("Connection Successful!")

	return previous_network


def get_gas_price(account):
	pka = network.account.PublicKeyAccount(account)
	prka = network.account._PrivateKeyAccount(pka)
	(gas_price, var1, var2 ) = prka._gas_price()
	time.sleep(1)
	return gas_price


def get_quote():
	chainlink_interface = json.load(open('interfaces/chainlink.json')) 
	eth_usd_oracle = network.main.web3.eth.contract(address="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419", abi=chainlink_interface)
	del chainlink_interface
	eth_price = eth_usd_oracle.caller.latestAnswer() / (10 ** 8)
	del eth_usd_oracle
	time.sleep(1)
	return eth_price