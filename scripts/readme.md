# Scripts and Add-Ons
Script descriptions and context for running them.
Scripts will default to moralis as a node provider if the moralis key is present. 

Sample .env:
```
export PRIVATE_KEY=<key>
export MORALIS_KEY=<key>
export WEB3_INFURA_PROJECT_ID=<key>
```

NOTICE: It's best to run these profiling scripts on Ropsten because it simulates the mainnet more closely

## preparation
Running the script generates a gas report template and simulates deployment with arguments found in 
constructor_arguments.py. This script OR evaluation.py must be ran before estimates or deploy. It also contains a function 
that allows you to ensure that the gas_report is there.

Example:
```
brownie run preparation --network ropsten
```
```
from .preparation import prepare 
from .constructor_arguments import DeploymentArguments

prepare(Token, DeploymentArguments, True/False)
``` 

In order to properly evaluate the smart contract, without writing an AI to unit test, a profiling function must be added
to contract_utils. The gas_profiler calls the execute method so any new contract to be profiled must be added to the list
of potential cases by their name string. 

Example:
```
def execute(name, contract, methods):
    profiled_methods = None
    match name:
        case "MonsterToken":
            profiled_methods = profile_mfc(contract, methods)
		case "NewToken": # added
			profiled_methods = profile_nt(contract, methods)
        case _:
            exit()
    return profiled_methods
```

In addition, the profiling function must be defined at the bottom with an import for its constructor arguments.

Example:
```
from .constructor_arguments import nt_args
def profile_nt(contract, methods):
	detect_free_(methods) # required
	
### DATA COLLECTION START

	contract.function_name_1(inputs, {"from": account1}) 				# first call
	mindex = get_mindex(methods, "function_name_1")
	methods[mindex] = update_method(methods[mindex])
	
	contract.function_name_1(reverse_inputs, {"from": account2})
	# time.sleep(1) # AFTER EVERY TX THAT DOES NOT USE update_method
	
	contract.function_name_2(inputs) 				# second call
	mindex = get_mindex(methods, "function_name_2")
	methods[mindex] = update_method(methods[mindex])
	methods[mindex + 1] = update_method(methods[mindex + 1]) # overloaded method has two entries
	
	
#   ... 											  more calls
	
	contract.function_name_n(inputs) 				# last call
	mindex = get_mindex(methods, "function_name_n")
	methods[mindex] = update_method(methods[mindex])

### DATA COLLECTION END
	
	return methods # required
```


## evaluation
Evaluates the cost of mainnet deployment and interaction. This can be run without running preparation.py. This script OR
preparation.py must be ran before estimates or deploy. It also contains a function that allows you to evaluate from other 
scripts instead of the terminal.

Example:
```
brownie run evaluation --network ropsten
```
```
from .preparation import prepare 
from .evaluation import evaluate
from .constructor_arguments import DeploymentArguments

prepare(Token, DeploymentArguments, True) # Resets
evaluate(Token, DeploymentArguments) # Populates
```


## estimates
Spits out quotes in ETH and USD amounts using the cached gas_reports. It saves time and energy. This script must be ran 
AFTER preparation OR evaluation. IF only preparation is run before estimates, it will skip method quotes.

Example:
```
brownie run estimates
```
```
from .estimates import estimation
from .constructor_arguments import DeploymentArguments

estimate(Token, DeploymentArguments)
```


## deployment 
Deploys the token after printing an estimate. It will print an error and exit if estimates are not available. It also contains 
a method for deployment via other scripts.  

Example:
```
brownie run deployment --network mainnet
... misc messages

Quote expires in 15 seconds...
Confirm deployment(y/n):
y 
Deployment confirmed!

... misc messages 
exit()
```
```
from .deployment import deploy
from .constructor_arguments import t_args

deploy(Token, t_args)
```


## gas_strategy
contains the new gas strategy as well as a method for quickly and easily updating the gas strategy. Calling reconnect from 
network_utils does this automatically. Running the script as main just diagnoses gas prices on the terminal. Use this if
your script does not contain a reconnect call.
```
.from gas_strategy import select_strategy

select_strategy()
```