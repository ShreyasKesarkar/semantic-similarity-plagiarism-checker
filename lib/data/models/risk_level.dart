/// Risk classification based on overall similarity score.
/// Matches the Risk Assessment Engine thresholds from the architecture doc:
/// 0–30% Low, 30–60% Medium, 60–100% High (thresholds are adjustable).
enum RiskLevel { low, medium, high }

extension RiskLevelX on RiskLevel {
  String get label {
    switch (this) {
      case RiskLevel.low:
        return 'Low Risk';
      case RiskLevel.medium:
        return 'Medium Risk';
      case RiskLevel.high:
        return 'High Risk';
    }
  }
}
