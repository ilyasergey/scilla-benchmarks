pragma solidity ^0.5.2;


contract Game {

  bytes32 winningHash;
  address payable owner;
  address payable playerA;
  address payable playerB;
  address payable winner;
  bytes32 playerAHash;
  bytes32 playerBHash;
  uint256 timer;
  uint256 rewardAmount;
  bool phase2Begun;
  bool playerASubmitted;
  bool playerBSubmitted;
  bool gameComplete;

  constructor(bytes32 _winningHash, address payable _playerA, address payable _playerB) public payable {
    owner = msg.sender;
    rewardAmount = msg.value;
    winningHash = _winningHash;
    playerA = _playerA;
    playerB = _playerB;
  }

  function hashDistance(bytes32 hashA, bytes32 hashB) public pure returns(uint256) {
    return uint(hashA) - uint(hashB);
  }
  
  modifier isPlayer() {
    require(msg.sender != playerA && msg.sender != playerB, "Not a player");
    _;
  }

  function updateTimer() private {
    timer = block.number + 11;
  }

  function submitGuessHash(bytes32 guess) public isPlayer {
    require(!phase2Begun);
    require(block.number < timer);

    bytes memory tempGuess = abi.encodePacked(guess);
    require(tempGuess.length != 0);

    bytes memory tempPlayerAHash = abi.encodePacked(playerAHash);
    bytes memory tempPlayerBHash = abi.encodePacked(playerBHash);

    if (msg.sender == playerA) {
      require(tempPlayerAHash.length == 0);
      playerAHash = guess;

      if (tempPlayerBHash.length != 0) {
        phase2Begun = true;
      } else {
        updateTimer();
      }
    } else {
      require(tempPlayerBHash.length == 0);
      playerBHash = guess;

      if (tempPlayerAHash.length != 0) {
        phase2Begun = true;
      } else {
        updateTimer();
      }
    }
  }

  function determineWinner() public view returns(address payable) {
    uint256 distanceA = hashDistance(winningHash, playerAHash);
    uint256 distanceB = hashDistance(winningHash, playerBHash);

    if (distanceA < distanceB) {
      return playerA;
    } else if (distanceB < distanceA) {
      return playerB;
    }
    return owner;
  }

  function submitGuessValue(bytes32 guessValue) public isPlayer {
    require(phase2Begun);
    bytes32 playerHash;

    if (msg.sender == playerA) {
      playerHash = playerAHash;
      require(!playerASubmitted);
    } else {
      playerHash = playerBHash;
      require(!playerBSubmitted);
    }

    bytes32 tempHash = keccak256(abi.encodePacked(guessValue));
    require(tempHash == playerHash);

    if (msg.sender == playerA) {
      playerASubmitted = true;
    } else {
      playerBSubmitted = true;
    }

    if (playerASubmitted && playerBSubmitted) {
      winner = determineWinner();
      gameComplete = true;
    }
  }

  function claimReward() public isPlayer {
    require(msg.sender == winner, "Not a winner");
    address(winner).transfer(rewardAmount);
  }

  function withdraw() public {
    require(msg.sender == owner);
    require(block.number >= timer + 30, "Not able to withdraw the amount yet");
    address(owner).transfer(rewardAmount);
  }

}
