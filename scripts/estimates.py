import os, json
from brownie import *
from .gas_profiler import GasReport
from .constructor_arguments import mfc_args


def estimation(contract, arguments):
	if not os.path.isdir("gas_reports"):
		print("\nERR: gas_reports not found! Please run preparation or evaluation before running this script.\n")
		exit()
	profiler = GasReport(contract, arguments)
	profiler.quote()


def main():
	estimation(MonsterToken, mfc_args)