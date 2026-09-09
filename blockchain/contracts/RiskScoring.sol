// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RiskScoring {

    struct RiskRecord {
        uint256 score;
        string riskLevel;
        uint256 timestamp;
    }

    mapping(address => RiskRecord) public riskRecords;

    event RiskScoreUpdated(
        address indexed user,
        uint256 score,
        string riskLevel
    );

    function calculateRisk(uint256 score) public {
        string memory level;

        if (score <= 30) {
            level = "Low";
        } else if (score <= 60) {
            level = "Medium";
        } else {
            level = "High";
        }

        riskRecords[msg.sender] = RiskRecord(
            score,
            level,
            block.timestamp
        );

        emit RiskScoreUpdated(msg.sender, score, level);
    }

    function getRisk(address user)
        public
        view
        returns (
            uint256 score,
            string memory riskLevel,
            uint256 timestamp
        )
    {
        RiskRecord memory record = riskRecords[user];

        return (
            record.score,
            record.riskLevel,
            record.timestamp
        );
    }
}
