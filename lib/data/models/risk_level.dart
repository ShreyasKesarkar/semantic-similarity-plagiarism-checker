/// Risk classification based on overall similarity score.
/// Matches the Risk Assessment Engine thresholds from the architecture doc:
/// 0–25% Low, 26–50% Medium, 51–75% High, 76-100% Very High
enum RiskLevel { low, medium, high, veryHigh }

extension RiskLevelX on RiskLevel {
  String get label {
    switch (this) {
      case RiskLevel.low:
        return 'Low Risk';
      case RiskLevel.medium:
        return 'Medium Risk';
      case RiskLevel.high:
        return 'High Risk';
      case RiskLevel.veryHigh:
        return 'Very High Risk';
    }
  }
}
