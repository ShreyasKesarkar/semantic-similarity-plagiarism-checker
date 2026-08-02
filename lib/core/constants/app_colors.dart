import 'package:flutter/material.dart';

import '../../data/models/risk_level.dart';

class AppColors {
  AppColors._();

  static const primary = Color(0xFF2563EB);
  static const background = Color(0xFFF8FAFC);
  static const cardBackground = Colors.white;
  static const textPrimary = Color(0xFF0F172A);
  static const textSecondary = Color(0xFF64748B);

  static const riskLow = Color(0xFF16A34A);
  static const riskMedium = Color(0xFFD97706);
  static const riskHigh = Color(0xFFEA580C);
  static const riskVeryHigh = Color(0xFFDC2626);

  static Color forRisk(RiskLevel level) {
    switch (level) {
      case RiskLevel.low:
        return riskLow;
      case RiskLevel.medium:
        return riskMedium;
      case RiskLevel.high:
        return riskHigh;
      case RiskLevel.veryHigh:
        return riskVeryHigh;
    }
  }
}
