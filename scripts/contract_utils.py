from brownie import *
import time


def execute(name, contract, methods):
    profiled_methods = None
    match name:
        case "MonsterToken":
            profiled_methods = profile_mfc(contract, methods)
        case _:
            exit()
    return profiled_methods


def detect_free_(methods):
    for method in methods:
        mutability = method["stateMutability"]
        if mutability != "nonpayable" and mutability != "payable":
            print("ERR: View or Pure function detected!")
            exit()


def get_mindex(methods, name):
    for method in methods:
        if method["function"] == name:
            return methods.index(method)


testnet_bank = accounts.add(config["wallets"]["testnet_key"])
testnet_bank2 = accounts.add(config["wallets"]["alt_testnet_key"])
def update_method(method):
    all_hist = history.from_sender(testnet_bank)
    this_receipt = all_hist[len(all_hist) - 1]
    method["gas_used"] = this_receipt.gas_used
    method["gas_limit"] = this_receipt.gas_limit
    method["gas_price"] = f'{int(this_receipt.gas_price / (10 ** 9))} gwei'
    time.sleep(1)

    return method


from .constructor_arguments import mfc_args
def profile_mfc(contract, methods):
    detect_free_(methods)
 
    contract.setBaseURI("something", {"from": testnet_bank})
    mindex = get_mindex(methods, "setBaseURI")
    methods[mindex] = update_method(methods[mindex])

    contract.setContractURI("something", {"from": testnet_bank})
    mindex = get_mindex(methods, "setContractURI")
    methods[mindex] = update_method(methods[mindex])

    contract.setApprovalForAll(testnet_bank2, True, {"from": testnet_bank})
    mindex = get_mindex(methods, "setApprovalForAll")
    methods[mindex] = update_method(methods[mindex])

    contract.toggleSaleState({"from": testnet_bank})
    mindex = get_mindex(methods, "toggleSaleState")
    methods[mindex] = update_method(methods[mindex])

    contract.toggleSaleState({"from": testnet_bank})
    time.sleep(1)

    contract.buyToken([1], {"from": testnet_bank, "value": mfc_args[6]})
    mindex = get_mindex(methods, "buyToken")
    methods[mindex] = update_method(methods[mindex])

    contract.release(mfc_args[2][0], {"from": testnet_bank})
    mindex = get_mindex(methods, "release")
    methods[mindex] = update_method(methods[mindex])

    contract.approve(testnet_bank2, 1, {"from": testnet_bank})
    mindex = get_mindex(methods, "approve")
    methods[mindex] = update_method(methods[mindex])

    contract.transferFrom(testnet_bank, testnet_bank2, 1, {"from": testnet_bank})
    mindex = get_mindex(methods, "transferFrom")
    methods[mindex] = update_method(methods[mindex])

    owned = False # debug
    while owned == False:
        owned = (contract.ownerOf(1) == testnet_bank2)
        time.sleep(1)

    contract.transferFrom(testnet_bank2, testnet_bank, 1, {"from": testnet_bank2})
    time.sleep(1)

    owned = False # debug
    while owned == False:
        owned = (contract.ownerOf(1) == testnet_bank)
        time.sleep(1)

    contract.safeTransferFrom(testnet_bank, testnet_bank2, 1, {"from": testnet_bank})
    mindex = get_mindex(methods, "safeTransferFrom")
    methods[mindex] = update_method(methods[mindex])
    methods[mindex + 1] = update_method(methods[mindex + 1])

    contract.transferOwnership(testnet_bank2, {"from": testnet_bank})
    mindex = get_mindex(methods, "transferOwnership")
    methods[mindex] = update_method(methods[mindex])

    owned = False # debug
    while owned == False:
        owned = (contract.owner() == testnet_bank2)
        time.sleep(1)

    contract.transferOwnership(testnet_bank, {"from": testnet_bank2})
    time.sleep(1)

    owned = False # debug
    while owned == False:
        owned = (contract.owner() == testnet_bank)
        time.sleep(1)

    contract.renounceOwnership({"from": testnet_bank})
    mindex = get_mindex(methods, "renounceOwnership")
    methods[mindex] = update_method(methods[mindex])

    return methods