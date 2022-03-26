import shutil, json
from brownie import *
from .gas_profiler import GasReport
from .constructor_arguments import mfc_args
from .network_utils import *
from .gas_strategy import select_strategy


def prepare(contract, arguments, reset):
	select_strategy()
	last_network = network.main.show_active()
	changed = False
	if "mainnet" in last_network.lower():
		last_network = reconnect(testnet_selector())
		changed = True

	if reset == True:
		print("Reset request detected! Clearing old data...")
		shutil.rmtree("gas_reports/")	
		print("Success!")
	
	profiler = GasReport(contract, arguments)
	profiler.profile_deployment()
	
	if changed == True:
		reconnect(last_network)


def main():
	prepare(MonsterToken, mfc_args, True)