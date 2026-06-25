// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// ============================================================
//  StoreRewards.sol
//  Project 4 — Store Rewards & Points
//  Technologies of Cryptocurrencies — HNU
// ============================================================
//  Core contract governing reward items, user registration,
//  redemptions, and emergency controls.
//  Roles (Owner / Admin / User) are enforced ON-CHAIN.
//  No OpenZeppelin. No external libraries.
// ============================================================

contract StoreRewards {

    // ----------------------------------------------------------
    //  Structs
    // ----------------------------------------------------------

    struct RewardItem {
        uint256 id;
        string  name;
        uint256 pointCost;
        uint256 stock;
        bool    active;
    }

    struct UserProfile {
        string  displayName;
        bool    registered;
        uint256 totalRedemptions;
    }

    // ----------------------------------------------------------
    //  State Variables
    // ----------------------------------------------------------

    // ── Role System (on-chain) ─────────────────────────────────
    address public owner;
    mapping(address => bool) public admins;
    mapping(address => bool) public users;

    bool    public paused;

    uint256 private _nextItemId;
    uint256 public  totalItemsCreated;
    uint256 public  totalRedemptions;

    mapping(uint256 => RewardItem)  public rewardItems;
    mapping(address => UserProfile) public userProfiles;
    mapping(address => bool)        public registeredUsers;

    mapping(address => mapping(uint256 => uint256)) public userRedemptionCount;

    address[] private _registeredAddresses;

    // ----------------------------------------------------------
    //  Events
    // ----------------------------------------------------------
    event OwnershipTransferred  (address indexed oldOwner,  address indexed newOwner);
    event AdminAdded            (address indexed admin,     address indexed by);
    event AdminRemoved          (address indexed admin,     address indexed by);
    event UserAdded             (address indexed user,      address indexed by);
    event UserRemoved           (address indexed user,      address indexed by);
    event ContractPaused        (address indexed by,        uint256 timestamp);
    event ContractResumed       (address indexed by,        uint256 timestamp);
    event RewardItemAdded       (uint256 indexed id,        string  name, uint256 pointCost, uint256 stock);
    event RewardItemUpdated     (uint256 indexed id,        string  name, uint256 pointCost, uint256 stock);
    event RewardItemDelisted    (uint256 indexed id,        address indexed by);
    event UserRegistered        (address indexed user,      string  name);
    event RewardEarned          (address indexed user,      uint256 amount);
    event RewardRedeemed        (address indexed user,      uint256 indexed itemId, string itemName, uint256 pointsSpent);
    event TokensTransferred     (address indexed from,      address indexed to, uint256 amount);
    event BatchItemsAdded       (uint256 count,             address indexed by);
    event AdminChanged          (address indexed oldAdmin,  address indexed newAdmin);  // legacy compat

    // ----------------------------------------------------------
    //  Modifiers
    // ----------------------------------------------------------

    modifier onlyOwner() {
        require(msg.sender == owner, "Owner only");
        _;
    }

    modifier onlyAdmin() {
        require(admins[msg.sender] || msg.sender == owner, "Admin only");
        _;
    }

    modifier onlyUser() {
        require(users[msg.sender] || registeredUsers[msg.sender], "User only");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "System paused");
        _;
    }

    modifier onlyRegistered() {
        require(registeredUsers[msg.sender], "StoreRewards: please register first");
        _;
    }

    // ----------------------------------------------------------
    //  Constructor
    // ----------------------------------------------------------
    constructor() {
        owner       = msg.sender;
        admins[msg.sender] = true;   // owner is also an admin
        paused      = false;
        _nextItemId = 1;
    }

    // ----------------------------------------------------------
    //  Admin View (legacy helper)
    // ----------------------------------------------------------
    function getAdmin() public view returns (address) {
        return owner;
    }

    // ----------------------------------------------------------
    //  Role Management (on-chain)
    // ----------------------------------------------------------

    /// @notice Grant admin rights to an address. Owner only.
    function addAdmin(address _admin) public onlyOwner {
        require(_admin != address(0), "Zero address");
        admins[_admin] = true;
        emit AdminAdded(_admin, msg.sender);
    }

    /// @notice Revoke admin rights from an address. Owner only.
    function removeAdmin(address _admin) public onlyOwner {
        admins[_admin] = false;
        emit AdminRemoved(_admin, msg.sender);
    }

    /// @notice Register an address as a normal user. Admin only.
    function addUser(address _user) public onlyAdmin {
        require(_user != address(0), "Zero address");
        users[_user] = true;
        emit UserAdded(_user, msg.sender);
    }

    /// @notice Remove a normal user. Admin only.
    function removeUser(address _user) public onlyAdmin {
        users[_user] = false;
        emit UserRemoved(_user, msg.sender);
    }

    // ----------------------------------------------------------
    //  Emergency Controls  (Owner only)
    // ----------------------------------------------------------

    function pauseSystem() public onlyOwner {
        require(!paused, "Already paused");
        paused = true;
        emit ContractPaused(msg.sender, block.timestamp);
    }

    function unpauseSystem() public onlyOwner {
        require(paused, "Not paused");
        paused = false;
        emit ContractResumed(msg.sender, block.timestamp);
    }

    // Legacy aliases
    function pause() public onlyOwner {
        require(!paused, "StoreRewards: already paused");
        paused = true;
        emit ContractPaused(msg.sender, block.timestamp);
    }

    function resume() public onlyOwner {
        require(paused, "StoreRewards: not currently paused");
        paused = false;
        emit ContractResumed(msg.sender, block.timestamp);
    }

    // ----------------------------------------------------------
    //  Ownership Transfer  (Owner only)
    // ----------------------------------------------------------

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Zero address");
        require(newOwner != owner, "Already owner");
        address oldOwner = owner;
        owner = newOwner;
        admins[newOwner] = true;   // grant admin to new owner
        admins[oldOwner] = false;  // revoke admin from old owner
        emit OwnershipTransferred(oldOwner, newOwner);
        emit AdminRemoved(oldOwner, newOwner);
        emit AdminChanged(oldOwner, newOwner);
    }

    // ----------------------------------------------------------
    //  Reward Item Management  (Admin only)
    // ----------------------------------------------------------

    function addRewardItem(
        string  calldata itemName,
        uint256 pointCost,
        uint256 stock
    ) public onlyAdmin returns (uint256) {
        require(bytes(itemName).length > 0, "Item name is empty");
        require(pointCost > 0,              "Point cost must be positive");
        require(stock > 0,                  "Stock must be positive");

        uint256 newId = _nextItemId++;
        rewardItems[newId] = RewardItem({
            id:        newId,
            name:      itemName,
            pointCost: pointCost,
            stock:     stock,
            active:    true
        });
        totalItemsCreated++;
        emit RewardItemAdded(newId, itemName, pointCost, stock);
        return newId;
    }

    function updateRewardItem(
        uint256 itemId,
        string  calldata newName,
        uint256 newPointCost,
        uint256 newStock
    ) public onlyAdmin {
        require(rewardItems[itemId].id != 0, "Item does not exist");
        require(bytes(newName).length > 0,   "Name cannot be empty");
        require(newPointCost > 0,            "Point cost must be positive");

        rewardItems[itemId].name      = newName;
        rewardItems[itemId].pointCost = newPointCost;
        rewardItems[itemId].stock     = newStock;
        emit RewardItemUpdated(itemId, newName, newPointCost, newStock);
    }

    function delistItem(uint256 itemId) public onlyAdmin {
        require(rewardItems[itemId].id != 0, "Item does not exist");
        require(rewardItems[itemId].active,  "Item already inactive");
        rewardItems[itemId].active = false;
        emit RewardItemDelisted(itemId, msg.sender);
    }

    function batchAddRewardItems(
        string[]  calldata names,
        uint256[] calldata pointCosts,
        uint256[] calldata stocks
    ) public onlyAdmin {
        require(names.length == pointCosts.length, "Array length mismatch");
        require(names.length == stocks.length,     "Array length mismatch");
        require(names.length > 0,                  "Empty batch");

        for (uint256 i = 0; i < names.length; i++) {
            require(bytes(names[i]).length > 0, "Batch entry has empty name");
            require(pointCosts[i] > 0,          "Batch entry has zero cost");
            require(stocks[i] > 0,              "Batch entry has zero stock");

            uint256 newId = _nextItemId++;
            rewardItems[newId] = RewardItem({
                id:        newId,
                name:      names[i],
                pointCost: pointCosts[i],
                stock:     stocks[i],
                active:    true
            });
            totalItemsCreated++;
            emit RewardItemAdded(newId, names[i], pointCosts[i], stocks[i]);
        }
        emit BatchItemsAdded(names.length, msg.sender);
    }

    // ----------------------------------------------------------
    //  User Registration
    // ----------------------------------------------------------

    function registerUser(string calldata displayName) public whenNotPaused {
        require(!registeredUsers[msg.sender],    "Address already registered");
        require(bytes(displayName).length > 0,   "Display name is empty");
        require(bytes(displayName).length <= 64, "Display name too long");

        registeredUsers[msg.sender] = true;
        users[msg.sender]           = true;
        userProfiles[msg.sender] = UserProfile({
            displayName:      displayName,
            registered:       true,
            totalRedemptions: 0
        });
        _registeredAddresses.push(msg.sender);
        emit UserRegistered(msg.sender, displayName);
    }

    // ----------------------------------------------------------
    //  User Tasks — Earn / Redeem / Transfer
    // ----------------------------------------------------------

    /// @notice Record that a user earned rewards (called by admin after minting).
    function earnRewards(address user, uint256 amount) public onlyAdmin {
        require(registeredUsers[user], "User not registered");
        emit RewardEarned(user, amount);
    }

    /// @notice Redeem a reward item (registered users only).
    function redeemReward(uint256 itemId) public whenNotPaused onlyRegistered {
        require(rewardItems[itemId].id != 0,   "Item does not exist");
        require(rewardItems[itemId].active,    "Item is not active");
        require(rewardItems[itemId].stock > 0, "Item is out of stock");

        rewardItems[itemId].stock                       -= 1;
        totalRedemptions                                += 1;
        userProfiles[msg.sender].totalRedemptions       += 1;
        userRedemptionCount[msg.sender][itemId]         += 1;

        // Auto-deactivate when stock reaches zero so the item is
        // immediately marked inactive on-chain and hidden from UIs.
        if (rewardItems[itemId].stock == 0) {
            rewardItems[itemId].active = false;
            emit RewardItemDelisted(itemId, msg.sender);
        }

        emit RewardRedeemed(
            msg.sender,
            itemId,
            rewardItems[itemId].name,
            rewardItems[itemId].pointCost
        );
    }

    // ----------------------------------------------------------
    //  View Functions  (Read-Only)
    // ----------------------------------------------------------

    function getRewardItem(uint256 itemId)
        public view
        returns (uint256, string memory, uint256, uint256, bool)
    {
        RewardItem storage item = rewardItems[itemId];
        require(item.id != 0, "Item does not exist");
        return (item.id, item.name, item.pointCost, item.stock, item.active);
    }

    function getTotalItems() public view returns (uint256) {
        return totalItemsCreated;
    }

    function getUserItemRedemptions(address user, uint256 itemId)
        public view returns (uint256)
    {
        return userRedemptionCount[user][itemId];
    }

    function getUserName(address user) public view returns (string memory) {
        require(registeredUsers[user], "User not registered");
        return userProfiles[user].displayName;
    }

    function getUserTotalRedemptions(address user) public view returns (uint256) {
        return userProfiles[user].totalRedemptions;
    }

    function getAllRegisteredUsers() public view returns (address[] memory) {
        return _registeredAddresses;
    }

    function getNextItemId() public view returns (uint256) {
        return _nextItemId;
    }

    function isAdmin(address _addr) public view returns (bool) {
        return admins[_addr] || _addr == owner;
    }

    function isUser(address _addr) public view returns (bool) {
        return users[_addr] || registeredUsers[_addr];
    }
}
