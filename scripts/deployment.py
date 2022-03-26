import os, json, time, datetime
from brownie import *


def _deploy_contract(contract, constructor_arguments):
    account = None 
    try: 
        account = accounts.add(config["wallets"]["from_mnemonic"])
    except:
        account = accounts.add(config["wallets"]["from_key"])

    if len(constructor_arguments) != 0:
        deployment_receipt = contract.deploy(*constructor_arguments, {'from': account})
    else:
        deployment_receipt = contract.deploy({'from': account})

    if not os.path.isdir("archive"):
        os.mkdir("archive")

    archive_folder = f'archive/deployments/{network.main.show_active()}/'
    if not os.path.isdir(archive_folder):
        os.mkdir(archive_folder)

    contract_folder = archive_folder + f'{contract._name}/'
    if not os.path.isdir(contract_folder):
        os.mkdir(contract_folder)

    filename = contract_folder + f'{datetime.date.today()}_{int(time.time())}.json'
    with open(filename, 'w+') as outfile:
        json.dump({
            contract._name: {
                "address": deployment_receipt.address,
                "abi": deployment_receipt.abi,
                },
            }, 
            outfile)

    print(f"saved to {filename}\n")


from .estimates import estimation
from .preparation import prepare
from .network_utils import reconnect, testnet_selector
from .gas_strategy import select_strategy
def deploy(contract, constructor_arguments):
    select_strategy()
    last = reconnect(testnet_selector())
    prepare(contract, constructor_arguments, True)
    reconnect(last)
    estimation(contract, constructor_arguments)
    os.remove(f"gas_reports/{contract._name}.json")
    quote_timestamp = int(time.time())

    while True:
        response = input("\nQuote Expires in 15 seconds...\nConfirm deployment (y/n):\n")
        if response.lower() != "y":
            print("Aborting deployment...\n")
            exit()
        else:
            print(f"Response processed in: {int(time.time()) - quote_timestamp} seconds...")
            break

    if int(time.time()) - quote_timestamp > 15:
        print("Quote Expired! Aborting deployment...\n")
        exit()
    else:
        print("Deployment confirmed!\n")
        _deploy_contract(contract, constructor_arguments)
        time.sleep(1)


from .constructor_arguments import mfc_args
def main():
    deploy(MonsterToken, mfc_args)