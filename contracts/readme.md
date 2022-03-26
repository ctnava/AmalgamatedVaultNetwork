# Contracts
Documentation of the Amalgamated Token Commerce Network

## Concept
The Vault Amalgam Network is a way to store gas, ERC20s, ERC1155s, and ERC721s in bundles.
It's components can be categorized into 3 distinguishable parts: the CORE, VAULTS, and SERVICES.
![](https://github.com/ctnava/AmalgamatedVaultNetwork/blob/main/contracts/blob/layout.png)

At it's CORE, Amalgamation Engine (VaultAmalgamator.sol) is the control center for, or is the heart of, 
the entire ecosystem, capable of replacing contracts as modules that it leans on for basic functions. 
It coordinates deposits and withdrawals to specialized VAULT contracts that store assets by contract
standard or class: gas(GasVault.sol), ERC20(TokenVault.sol), ERC1155(SftVault.sol), and ERC721(NftVault.sol). 
These components together power the client-facing SERVICE contracts (AuctionHouse.sol, MarketPlace.sol, and not 
limited to AssetLocker.sol).

Services powered by this ecosystem directly interact with the core contract to sort and store asset bundles in the 
appropriate vaults, while also storing an open record of activity on itself. Each bundle is labeled with an address
for the service provider; meaning that the core contract will only allow service contracts to interact with deposits 
that they have registered.
![](https://github.com/ctnava/AmalgamatedVaultNetwork/blob/main/contracts/blob/asset_flow.png)

In the event that a vault must be ejected (for upgrades), asset owners may still retrieve their belongings because
vaults not only hold the assets, but also maintain a public record of ownership. In addition, the core contract 
also maintains a transparent record of where all of the bundles are stored. This storage redundancy is meant to act 
as a paper trail so that clients never lose their property, even if the vaults are discarded because the process of 
jettisoning these components restricts all activity to a "Withdraw Only" state.

As a precautionary measure, all fallbacks revert.

## Services, Pricing Models, & Revenue Flow
Service contracts will contain their own pricing and payment structure, the details of which are posted below. All
token and gas proceeds are paid to the ultimate authority over the VaultAmalgamator (via the 2-Factor NFT system or 
Ownable.sol).

### AssetLocker.sol 
The asset locker provides a way to obscure or forcibly hold tokens. This is useful for crowdsales, inheritance, college
funds, and more. By simply providing an "owner" address, you can ensure that these assets will be reserved for whomever 
you desire, whenever you wish; with no risk of having them lent out. In a nutshell, this is an automated asset custodian. 

Lockers are rented at a non-refundable rate of 10 Gwei/second (or 0.03154 ETH/ year) with the ability to retrieve assets
prematurely. Alternatively, a rate of 5 Gwei/second (or 0.01577 ETH/ year) is available for deposits that will not be
retrievable before the timer expires. There is no fee for retrieval.

### MarketPlace.sol 
This market place handles private, public, ERC20, ERC721, ERC1155, gas, and hybridized escrows. The MarketPlace contract 
provides a way to easily list large amounts of various assets for a seamless peer-to-peer trading experience. Listings 
(called 'offers') are subject to a creation fee, payable in LOGO, and cost nothing to take. 

### AuctionHouse.sol 
Auction off ERC721s, ERC20s, ERC1155s, gas, and mixed lots. There is no fee to start an auction; but once it's started, it 
can't be stopped. Allow the auction to be done in gas, erc20s, or both! There are no fees for winning and a portion of the 
winning bid is subtracted as a service fee before going to the client upon conclusion or claim.

## Roadmap
This is a progress report and status of all contracts. In order to properly begin beta testing, at least one vault and 
service must be complete; alongside the core. The core will not be fully complete until all potential vaults are. This 
system must see CORE deployment first, VAULT deployment second, and SERVICE deployment last. After initial deployment,
additional SERVICE contracts may be continuously added with no need to eject; as they all lean on the CORE for function.

```
{
	"category":
		"CORE": {
			"VaultAmalgamator.sol": {
				"contract": "CONTINUOUS DEVELOPMENT",
				"unit testing": "CONTINUOUS DEVELOPMENT",
				"gas profiling": "CONTINUOUS DEVELOPMENT",
				"deployment script": "CONTINUOUS DEVELOPMENT",
			}
		},
		
		"VAULTS": {
			"GasVault.sol": {
				"contract": null,
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
			
			"TokenVault.sol": {
				"contract": "complete",
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
			
			"NftVault.sol": {
				"contract": "complete",
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
			
			"SftVault.sol": {
				"contract": null,
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
		},
		
		"SERVICES": {
			"AuctionHouse.sol": {
				"contract": null,
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
			
			"MarketPlace.sol": {
				"contract": null,
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
			
			"AssetLocker.sol": {
				"contract": null,
				"unit testing": null,
				"gas profiling": null,
				"deployment script": null,
			},
		}
	
}	
```

