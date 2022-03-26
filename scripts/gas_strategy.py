import threading, time, warnings, requests, brownie
from typing import Dict, Generator
from brownie.convert import Wei
from brownie.network.gas.bases import BlockGasStrategy, SimpleGasStrategy, TimeGasStrategy
from brownie import network, config


dpi_api_key = config["api"]["defi_pulse"]
etherscan_api_key = config["api"]["etherscan"]
"""
Gas strategies for determing a price using DefiPulse's ethgasstation API.
with an api key from https://data.defipulse.com/.

URL:        https://data-api.defipulse.com/api/v1/egs/api/ethgasAPI.json?api-key={api_key}

DefiPulse returns 4 possible prices:
NOTICE: gas price in x10 Gwei (divide by 10 to convert it to gwei)

fastest:    expected to be mined in < 30 seconds
fast:       expected to be mined in < 2 minutes
average:    expected to be mined in < 5 minutes
safeLow:    expected to be mined in < 30 minutes

This endpoint also returns their wait times (in minutes):
["fastestWait", "fastWait", "avgWait", "safeLowWait"]

Other misc information:
block_time: average time (seconds) to mine one block
speed:      smallest value of (gasUsed/gasLimit) from last 10 blocks
blockNum:   latest block number

Visit https://docs.ethgasstation.info/ for more information on how this API
calculates gas prices.
"""
_gasnow_update = 0
_gasnow_data: Dict[str, int] = {}
_gasnow_lock = threading.Lock()
def _fetch_gasnow(key: str) -> int:
    global _gasnow_update
    current_network = network.main.show_active()
    mainnet_result = ("mainnet" in current_network)

    with _gasnow_lock:
        time_since_update = int(time.time() - _gasnow_update)
        if time_since_update > 15:
            try:
                response = None
                data = None
                
                if mainnet_result:
                    response = requests.get(f"https://data-api.defipulse.com/api/v1/egs/api/ethgasAPI.json?api-key={dpi_api_key}") # "https://etherchain.org/api/gasnow" 
                else:
                    modifier = ""
                    if "-m" in current_network:
                        modifier = current_network[:current_network.index("-")]
                    response = requests.get(f"https://api-{modifier}.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscan_api_key}") # -{modifier}
                
                response.raise_for_status()
                data = response.json() if mainnet_result else response.json()["result"]

                
                _gasnow_update = int(time.time()) # data.pop("timestamp") // 1000
                _gasnow_data.update(data)
            except requests.exceptions.RequestException as exc:
                if time_since_update > 120:
                    raise
                warnings.warn(
                    f"{type(exc).__name__} while querying DefiPulse's GasStation API. "
                    f"Last successful update was {time_since_update}s ago.",
                    RuntimeWarning,
                )

    result = _gasnow_data[key] * (10 ** 8) if mainnet_result else None

    if result == None:
        order = ["fastest", "fast", "average", "safeLow"]
        index_k = order.index(key)

        match key:
            case "fastest":
                result = int(_gasnow_data["FastGasPrice"]) * (10 ** 9)
            case "fast":
                result = int(_gasnow_data["FastGasPrice"]) * (10 ** 9)
            case "average":
                result = int(_gasnow_data["ProposeGasPrice"]) * (10 ** 9)
            case "safeLow":
                result = int(_gasnow_data["SafeGasPrice"]) * (10 ** 9)
            case _:
                raise ValueError("ERROR: Unexpected Gas Type")

    return result


def check_key(speed, label):
    if speed not in ("fastest", "fast", "average", "safeLow"):
        raise ValueError(f"ERROR: {label} must be one of: fastest, fast, average, safeLow")
    if speed == "safeLow":
        print(f"WARNING: {label} is set to safeLow (Not Recommended)")


class DefiPulseStrategy(SimpleGasStrategy): # BROADCAST ONCE ONLY
    def __init__(self, speed: str = "average"):
        check_key(speed, "`speed`")
        self.speed = speed

    def get_gas_price(self) -> int:
        return _fetch_gasnow(self.speed)


def ensure_increasing(initial_speed, max_speed):
    order = ["fastest", "fast", "average", "safeLow"]
    index_i = order.index(initial_speed)
    index_m = order.index(max_speed)
    if index_i == index_m:
        raise ValueError("ERROR: initial_speed is max_speed")
    if index_m > index_i:
        raise ValueError("ERROR: initial_speed is slower than max_speed")

class DefiPulseScalingStrategy(BlockGasStrategy): # REBROADCAST EVERY BLOCK
    """
    The initial gas price is set according to `initial_speed`. The gas price
    for each subsequent transaction is increased by multiplying the previous gas
    price by `increment`, or increasing to the current `initial_speed` gas price,
    whichever is higher. No repricing occurs if the new gas price would exceed
    the current `max_speed` price as given by the API.
    """
    def __init__(self, 
        initial_speed: str = "safeLow", max_speed: str = "fastest", 
        increment: float = 1.125, block_duration: int = 2,
        max_gas_price: Wei = None,
    ):
        check_key(initial_speed, "`initial_speed`")
        check_key(max_speed, "`max_speed`")
        ensure_increasing(initial_speed, max_speed)

        super().__init__(block_duration)
        self.initial_speed = initial_speed
        self.max_speed = max_speed
        self.increment = increment
        self.max_gas_price = Wei(max_gas_price) or 2 ** 256 - 1

    def get_gas_price(self) -> Generator[int, None, None]:
        last_gas_price = _fetch_gasnow(self.initial_speed)
        yield last_gas_price

        while True:
            # increment the last price by `increment` or use the new
            # `initial_speed` value, whichever is higher
            initial_gas_price = _fetch_gasnow(self.initial_speed)
            incremented_gas_price = int(last_gas_price * self.increment)
            new_gas_price = max(initial_gas_price, incremented_gas_price)

            # do not exceed the current `max_speed` price
            max_gas_price = _fetch_gasnow(self.max_speed)
            last_gas_price = min(max_gas_price, new_gas_price, self.max_gas_price)
            yield last_gas_price


from brownie.network.gas.strategies import ExponentialScalingStrategy
custom_strategy = ExponentialScalingStrategy(initial_gas_price="15 gwei", max_gas_price="150 gwei", time_duration=15)
def select_strategy():
    current_network = network.main.show_active()
    if "development" != current_network:
        if "mainnet" in current_network:
            print("\nMainnet Strategy Loaded!\nDiagnosing DefiPulse Output...")
            print(f'|| safeLow:            {int(DefiPulseStrategy("safeLow").get_gas_price() / (10 ** 9))} Gwei')
            print(f'|| average(default):   {int(DefiPulseStrategy().get_gas_price() / (10 ** 9))} Gwei')
            print(f'|| fast(selected):     {int(DefiPulseStrategy("fast").get_gas_price() / (10 ** 9))} Gwei')
            print(f'|| fastest:            {int(DefiPulseStrategy("fastest").get_gas_price() / (10 ** 9))} Gwei\n')
            network.gas_price(DefiPulseStrategy("fast"))
        else:
            print("\nTestnet Strategy Loaded!\nDiagnosing Custom Time-Based Strategy...")
            print(f'|| initial_gas_price:   {int(next(custom_strategy.get_gas_price()) / (10 ** 9))}  Gwei')
            print(f'|| max_gas_price:       {int(custom_strategy.max_gas_price / (10 ** 9))} Gwei\n')
            network.gas_price(custom_strategy)
    else:
        print("\nNo custom gas strategy for DevNet\n")


def main():
    print("\nDiagnosing DefiPulse Output...")
    print(f'|| safeLow:            {int(DefiPulseStrategy("safeLow").get_gas_price() / (10 ** 9))} Gwei')
    print(f'|| average(default):   {int(DefiPulseStrategy().get_gas_price() / (10 ** 9))} Gwei')
    print(f'|| fast:               {int(DefiPulseStrategy("fast").get_gas_price() / (10 ** 9))} Gwei')
    print(f'|| fastest:            {int(DefiPulseStrategy("fastest").get_gas_price() / (10 ** 9))} Gwei\n')

    print("\nDiagnosing Custom Time-Based Strategy...")
    print(f'|| initial_gas_price:   {int(next(custom_strategy.get_gas_price()) / (10 ** 9))}  Gwei')
    print(f'|| max_gas_price:       {int(custom_strategy.max_gas_price / (10 ** 9))} Gwei\n')

    print("\nNo custom gas strategy for DevNet\n")