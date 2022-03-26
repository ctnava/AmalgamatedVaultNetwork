import os, json
from brownie import *
from .gas_profiler import GasReport
from .constructor_arguments import mfc_args
from .network_utils import dev_check
from .gas_strategy import select_strategy


def evaluate(contract, arguments):
	select_strategy()
	dev_check()
	if "mainnet" in  network.main.show_active().lower():
		print("\nERROR: Aborting Evaluation... Mainnet selected\n")
		exit()
	profiler = GasReport(contract, arguments)
	profiler.profile()

def main():
	evaluate(MonsterToken, mfc_args)