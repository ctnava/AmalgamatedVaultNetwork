// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

abstract contract GuardedVault {
	string public constant vaErr = "GuardedVault: Sender not VaultAmalgamator";
	address public vaultAmalgamator;
	constructor(address _vaultAmalgamator) { vaultAmalgamator = _vaultAmalgamator; }


	modifier AmalgamatorOnly() { 
		require(msg.sender == vaultAmalgamator, vaErr);_; }


	bool public attached = true;
	function toggleState() public AmalgamatorOnly { 
		attached = !attached; }
}