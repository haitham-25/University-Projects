// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// ============================================================
//  RewardPointCoin.sol
//  Project 4 — Store Rewards & Points
//  Technologies of Cryptocurrencies — HNU
// ============================================================
//  A fully hand-written ERC-20 token.
//  No OpenZeppelin. No external libraries.
//  The Admin (deployer / owner) is the sole minting authority.
//  On-chain ownership enforced via onlyAdmin modifier.
// ============================================================

contract RewardPointCoin {

    // ----------------------------------------------------------
    //  Token Metadata
    // ----------------------------------------------------------
    string  public name     = "Reward Point Coin";
    string  public symbol   = "RPC";
    uint8   public decimals = 18;
    uint256 public totalSupply;

    // ----------------------------------------------------------
    //  State Variables
    // ----------------------------------------------------------
    address public owner;   // Primary owner (set in constructor)

    mapping(address => uint256)                     public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    // ----------------------------------------------------------
    //  Events
    // ----------------------------------------------------------
    event Transfer    (address indexed from,     address indexed to,      uint256 value);
    event Approval    (address indexed owner,    address indexed spender, uint256 value);
    event Minted      (address indexed to,       uint256 amount,          uint256 newTotalSupply);
    event Burned      (address indexed from,     uint256 amount);
    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);

    // ----------------------------------------------------------
    //  Modifiers
    // ----------------------------------------------------------
    modifier onlyAdmin() {
        require(msg.sender == owner, "Admin only");
        _;
    }

    // ----------------------------------------------------------
    //  Constructor
    // ----------------------------------------------------------
    constructor() {
        owner = msg.sender;
    }

    // ----------------------------------------------------------
    //  Admin View
    // ----------------------------------------------------------
    function getAdmin() public view returns (address) {
        return owner;
    }

    // ----------------------------------------------------------
    //  ERC-20 Core
    // ----------------------------------------------------------

    function transfer(address to, uint256 amount) public returns (bool) {
        require(to != address(0),               "RPC: transfer to zero address");
        require(balanceOf[msg.sender] >= amount, "RPC: insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to]         += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) public returns (bool) {
        require(spender != address(0), "RPC: approve to zero address");
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        require(from != address(0),                        "RPC: transfer from zero address");
        require(to   != address(0),                        "RPC: transfer to zero address");
        require(balanceOf[from] >= amount,                 "RPC: insufficient balance");
        require(allowance[from][msg.sender] >= amount,     "RPC: allowance exceeded");
        allowance[from][msg.sender] -= amount;
        balanceOf[from]             -= amount;
        balanceOf[to]               += amount;
        emit Transfer(from, to, amount);
        return true;
    }

    // ----------------------------------------------------------
    //  Admin-Only Operations  (on-chain enforced)
    // ----------------------------------------------------------

    /// @notice Mint new tokens to any address. ONLY Admin.
    function mint(address to, uint256 amount) public onlyAdmin {
        require(to != address(0), "RPC: mint to zero address");
        require(amount > 0,       "RPC: mint amount must be positive");
        totalSupply   += amount;
        balanceOf[to] += amount;
        emit Minted(to, amount, totalSupply);
        emit Transfer(address(0), to, amount);
    }

    /// @notice Burn tokens from any address. ONLY Admin.
    function burn(address from, uint256 amount) public onlyAdmin {
        require(from != address(0),        "RPC: burn from zero address");
        require(balanceOf[from] >= amount,  "RPC: burn exceeds balance");
        balanceOf[from] -= amount;
        totalSupply     -= amount;
        emit Burned(from, amount);
        emit Transfer(from, address(0), amount);
    }

    /// @notice Transfer admin rights to a new address.
    function transferAdminship(address newAdmin) public onlyAdmin {
        require(newAdmin != address(0), "RPC: new admin is zero address");
        address oldAdmin = owner;
        owner = newAdmin;
        emit AdminChanged(oldAdmin, newAdmin);
    }
}
