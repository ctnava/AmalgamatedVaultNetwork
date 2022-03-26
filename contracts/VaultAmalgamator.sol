// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./vaults/TokenVault.sol";
import "./vaults/NftVault.sol";


contract VaultAmalgamator {
	string constant public name = "VaultAmalgamator";
	uint constant max_uint = (2 ** 255) + ((2 ** 255) - 1);
	address constant null_addr = 0x0000000000000000000000000000000000000000;

	TokenVault 	public tokenVault;
	NftVault 	public nftVault;
	function registerVaults(address _tokenVault, address _nftVault) public {
		require(_tokenVault != null_addr || _nftVault != null_addr); 			// change at least one vault
		
		if(_tokenVault != null_addr) { 
			if(address(tokenVault) != null_addr) { tokenVault.toggleState(); } 	// deactivate old vault to allow withdrawals
			tokenVault = TokenVault(_tokenVault); }								// register new token vault

		if(_nftVault != null_addr) { 
			if(address(nftVault) != null_addr) { nftVault.toggleState(); } 		// deactivate old vault to allow withdrawals
			nftVault = NftVault(_nftVault); } } 								// register new nft vault


	struct DepositBundle {
		address tVault;
		address nVault;
		uint[] tDeposits;
		uint[] nDeposits;
		address owner;
		uint status; } //enum DepositState { Undefined, Deposited, Withdrawn, Claimed }
	mapping(uint => DepositBundle) internal bundles;
	uint public num_bundles;
	

	modifier ValidBundle(uint bundleId) { 
		require(bundles[bundleId].status != 0, "VaultAmalgamator: Query for nonexistent bundle.");_; }


	function bundle(uint bundleId) public view ValidBundle(bundleId) returns(DepositBundle memory) { 
		return bundles[bundleId]; }

	function ownerOf(uint bundleId) public view returns(address owner) { 
		return bundle(bundleId).owner; }

	function assetsOf(uint bundleId) public view returns(uint[] memory tDeposits, uint[] memory nDeposits) { 
		return (bundle(bundleId).tDeposits, bundle(bundleId).nDeposits); }

	function statusOf(uint bundleId) public view returns(uint status) { 
		return bundle(bundleId).status; }


	constructor() {}


	modifier Authorized(uint bundleId) {
		require(tx.origin == ownerOf(bundleId), "VaultAmalgamator: Caller not owner");_;}

	modifier StateMatch(uint state, uint bundleId) { 
		require(statusOf(bundleId) == state, "VaultAmalgamator: Invalid Deposit State");_; }


	function claimBundle(uint bundleId, address receiver, uint new_state) public Authorized(bundleId) StateMatch(1, bundleId) {
		require(new_state == 2 || new_state == 3);
		(uint[] memory tDeposits, uint[] memory nDeposits) = assetsOf(bundleId);
		
		for(uint i = 0; i < tDeposits.length; i++) {
			tokenVault.retrieveDeposit(tDeposits[i], receiver, new_state); }

		for(uint i = 0; i < nDeposits.length; i++) {
			nftVault.retrieveDeposit(nDeposits[i], receiver, new_state); }

		bundles[bundleId].status = new_state; }


	function registerBundle(address[] memory tokens, uint[] memory values, address[] memory nfts, uint[] memory ids, address owner) public returns(uint bundleId) {
		require(tokens.length == values.length && nfts.length == ids.length, "VaultAmalgamator: length mismatch");
		require(owner != null_addr);
		
		num_bundles++;
		bundles[num_bundles] = DepositBundle(address(tokenVault), address(nftVault), new uint[](0), new uint[](0), owner, 1);

		for(uint i = 0; i < tokens.length; i++) { 
			ERC20(tokens[i]).transferFrom(msg.sender, address(tokenVault), values[i]);
			bundles[num_bundles].tDeposits.push(tokenVault.registerDeposit(tokens[i], values[i], owner)); }

		for(uint i = 0; i < tokens.length; i++) { 
			ERC721(nfts[i]).transferFrom(msg.sender, address(nftVault), ids[i]);
			bundles[num_bundles].nDeposits.push(nftVault.registerDeposit(nfts[i], ids[i], owner)); }

		return num_bundles; }

}