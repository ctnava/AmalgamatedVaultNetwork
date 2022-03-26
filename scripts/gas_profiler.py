import os, json, time
from brownie import *
from .network_utils import *
from .contract_utils import execute


testnet_bank = accounts.add(config["wallets"]["testnet_key"])
def report_fee(consumption, limit, eth_quote, gas_rate):
	wei_cost_c = (consumption * gas_rate)
	cost = wei_cost_c / (10 ** 18)
	print("|| Consumption Fee: " + str(cost) + " ETH")

	usd_value_c = cost * eth_quote
	usd_string = str(usd_value_c)
	print("|| Approx. USD Value: $" + usd_string[:usd_string.index(".") + 3])

	wei_cost_l = (limit * gas_rate)
	cost = wei_cost_l / (10 ** 18)
	print("|| Max Fee: " + str(cost) + " ETH")

	usd_value_l = cost * eth_quote
	usd_string = str(usd_value_l)
	print("|| Approx. USD Value: $" + usd_string[:usd_string.index(".") + 3] + "\n")

	return (wei_cost_c, usd_value_c, wei_cost_l, usd_value_l)


class GasReport:
	def __init__(self, this_project, constructor_arguments):
		self.project = this_project 
		self.name = this_project._name
		print("\nProfiling " + self.name + "...")

		self.path = "gas_reports/" + self.name + '.json'
		if not os.path.isdir("gas_reports"):
			os.mkdir("gas_reports")
		self.exists = os.path.isfile(self.path)

		data = self.retrieve() if self.exists else json.loads('{"gas_used": null, "gas_limit": null, "gas_price": null, "address": null, "constructor_arguments": null, "methods": null}')
		build_json = json.load(open('build/contracts/' + self.name + '.json'))
		methods = []
		if self.exists:
			methods = data["methods"] 
		else:
			abi = build_json["abi"]
			for function in abi:
				if function["type"] == "function":
					if function["stateMutability"] != "pure" and function["stateMutability"] != "view":
						method = json.loads('{"function": null, "gas_used": null, "gas_limit": null, "gas_price": null, "stateMutability": null, "inputs": null, "outputs": null}')
						method['function'] = function['name']
						method['stateMutability'] = function['stateMutability']
						method['inputs'] = function['inputs']
						method['outputs'] = function['outputs']
						methods.append(method)
			data["methods"] = methods

		same_methods = True
		for method in methods:
			if method["gas_used"] == None or method["gas_limit"] == None:
				same_methods = False

		same_constructor = False
		if data["constructor_arguments"] != None:
			same_constructor = (len(constructor_arguments) == len(data["constructor_arguments"]))

		if same_constructor:
			for arg in constructor_arguments:
				aindex = constructor_arguments.index(arg)
				stored = data["constructor_arguments"][aindex]
				if type(arg) != type(stored):
					same_constructor = False
				if type(arg) == type([1, 2, 3]):
					for value in arg:
						vindex = arg.index(value)
						if type(value) != type(stored[vindex]):
							same_constructor = False

		if not self.exists or not same_constructor or not same_methods:
			if not self.exists:
				print("Gas Report not Found... Generating Template")
			else:
				if not same_constructor:
					print("Constructor Behavior changed... Generating Template")
				else:
					print("Method change detected... Generating Template")

			data["constructor_arguments"] = constructor_arguments
			data["methods"] = methods
			self.save(data, "Initialized")

		else:
			print("Ready")

		self.contract = None

	
	def retrieve(self):
		return json.load(open(self.path))
	

	def save(self, data, arg):
		outfile = open(self.path, "w+")
		outfile.write(json.dumps(data, indent=4))
		outfile.close()
		print(self.name + " Gas Profile " + arg + "!\n")


	def profile_deployment(self):
		if "mainnet" in network.main.show_active().lower():
			print("ABORTED: Cannot profile on mainnet!")
			exit()

		data = self.retrieve()
		this_project = self.project
		with_args = data["constructor_arguments"]

		if len(with_args) == 0:
			self.contract = testnet_bank.deploy(this_project)
		else:
			self.contract = testnet_bank.deploy(this_project, *with_args)
		time.sleep(1)
		
		all_hist = history.from_sender(testnet_bank)
		this_receipt = all_hist[len(all_hist) - 1]
		data["gas_used"] = this_receipt.gas_used
		data["gas_limit"] = this_receipt.gas_limit
		data["gas_price"] = f'{int(this_receipt.gas_price / (10 ** 9))} gwei'
		data["address"] = self.contract.address
		self.save(data, "Updated")
		print("WARNING: Hand-written unit tests are required to profile method costs.\n")


	def profile_methods(self):
		if "mainnet" in network.main.show_active().lower():
			print("ABORTED: Cannot profile on mainnet!")
			exit()
			
		data = self.retrieve()
		addr = data["address"]
		profiled_methods = execute(self.name, self.contract, data["methods"])

		if profiled_methods == None:
			print("ERR: Hand-written unit tests are required to profile method costs! Exiting...")
			exit()

		data["methods"] = profiled_methods
		self.save(data, "Updated")


	def quote_deployment_cost(self, eth_quote, gas_rate):
		data = self.retrieve()
		consumption = data["gas_used"]
		limit = data["gas_limit"]
		print("---------- START REPORT ----------\n\nTxType: DEPLOYMENT")
		(wei_cost_c, usd_value_c, wei_cost_l, usd_value_l) = report_fee(consumption, limit, eth_quote, gas_rate)


	def quote_methods_cost(self, eth_quote, gas_rate):
		data = self.retrieve()
		methods = data["methods"]
		for method in methods:
			if method['gas_used'] == None or method['gas_limit'] == None:
				print("WARNING: Method quotes skipped! Unit tests not configured.\n")
				break
			print("TxType: " + method["function"])
			(wei_cost_c, usd_value_c, wei_cost_l, usd_value_l) = report_fee(method['gas_used'], method['gas_limit'], eth_quote, gas_rate) # 
			

	def quote(self):
		previous = reconnect(mainnet_selector())
		eth_quote = get_quote()
		gas_rate = get_gas_price(testnet_bank)
		gas_string = str(gas_rate / (10 ** 9))
		print("\nEstimating Mainnet Fees for " + self.name + "... || Gas Rate: " + gas_string[:gas_string.index(".")] + " Gwei")

		self.quote_deployment_cost(eth_quote, gas_rate)
		self.quote_methods_cost(eth_quote, gas_rate)
		print("---------- END REPORT ----------\n")
		reconnect(previous)
		

	def profile(self):
		last_network = network.main.show_active()
		if "mainnet" in last_network.lower():
			last_network = reconnect(testnet_selector())
		self.profile_deployment()
		self.profile_methods()
		self.quote()
		reconnect(last_network)
		