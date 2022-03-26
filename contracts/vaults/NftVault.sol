// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./GuardedVault.sol";


contract NftVault is GuardedVault {
	string public name = "NftVault";

    struct TokenDeposit {
    	ERC721 asset;
    	uint id;
    	address owner;
    	uint status; } //enum DepositState { Undefined, Deposited, Withdrawn, Claimed }

    mapping(uint => TokenDeposit) internal deposits;
    uint public num_deposits;

    modifier ValidDeposit(uint depositId) { 
    	require(deposits[depositId].status != 0, "NftVault: Query for nonexistent deposit.");_; }

    function deposit(uint depositId) public view ValidDeposit(depositId) returns(TokenDeposit memory thisDeposit) { 
    	return deposits[depositId]; }

	function ownerOf(uint depositId) public view returns(address owner) { 
		return deposit(depositId).owner; }

	function assetOf(uint depositId) public view returns(ERC721 asset) { 
		return deposit(depositId).asset; }

	function valueOf(uint depositId) public view returns(uint value) { 
		return deposit(depositId).id;}

	function statusOf(uint depositId) public view returns(uint status) { 
		return deposit(depositId).status; }
		

    constructor(address _vaultAmalgamator) GuardedVault(_vaultAmalgamator) {  }


    modifier Authorized(uint depositId) {
		if(attached == true) {
			require(msg.sender == vaultAmalgamator, vaErr);_; }
		else {
			require(msg.sender == ownerOf(depositId));_; } }


	modifier StateMatch(uint state, uint depositId) { 
		require(statusOf(depositId) == state, "TokenVault: Invalid Deposit State");_; }


	function retrieveDeposit(uint depositId, address receiver, uint new_state) public Authorized(depositId) StateMatch(1, depositId) {
		require(new_state == 2 || new_state == 3);
		ERC721 asset = assetOf(depositId);
		uint value = valueOf(depositId);
		address this_addr = address(this);

		asset.approve(this_addr, value);
		asset.transferFrom(this_addr, receiver, value); 
		new_state = (attached == false) ? 2 : new_state;
		deposits[depositId].status = new_state; }


	function registerDeposit(address asset, uint value, address owner) public AmalgamatorOnly returns(uint depositId) {
		num_deposits++;
		// AMALGAMATOR MUST DEPOSIT ASSET
		deposits[num_deposits] = TokenDeposit(ERC721(asset), value, owner, 1);
		return num_deposits; }
}