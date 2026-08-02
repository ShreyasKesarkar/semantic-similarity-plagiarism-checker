import '../../data/models/risk_level.dart';

class AiExplanationGenerator {
  static String generateExplanation(RiskLevel level, double similarityPercent) {
    switch (level) {
      case RiskLevel.low:
        return 'The documents exhibit minimal similarity ($similarityPercent%). The matched content is likely standard terminology or common phrases.';
      case RiskLevel.medium:
        return 'Moderate similarity detected ($similarityPercent%). There are some overlapping sections that may require a quick review for proper citations, but overall structure appears distinct.';
      case RiskLevel.high:
        return 'High similarity detected ($similarityPercent%). The documents share significant overlapping content, suggesting heavy paraphrasing or direct copying of substantial sections.';
      case RiskLevel.veryHigh:
        return 'Very high similarity detected ($similarityPercent%). A vast majority of the content is identical or trivially altered. Strongly indicative of plagiarism or duplicates.';
    }
  }
}
