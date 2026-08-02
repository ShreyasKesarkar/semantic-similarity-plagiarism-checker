import 'matched_sentence_pair.dart';
import 'risk_level.dart';

/// The full result of comparing Document A and Document B.
/// This is the shape your FastAPI backend should eventually return
/// from POST /compare (or similar endpoint).
class SimilarityResultModel {
  final String id; // unique id for this check (useful for history/dashboard)
  final String documentAName;
  final String documentBName;
  final double overallSimilarityPercent; // 0–100
  final RiskLevel riskLevel;
  final List<MatchedSentencePair> matchedSections;
  final String recommendation;
  final DateTime checkedAt;

  SimilarityResultModel({
    required this.id,
    required this.documentAName,
    required this.documentBName,
    required this.overallSimilarityPercent,
    required this.riskLevel,
    required this.matchedSections,
    required this.recommendation,
    required this.checkedAt,
  });

  factory SimilarityResultModel.fromJson(Map<String, dynamic> json) {
    return SimilarityResultModel(
      id: json['id'] as String,
      documentAName: json['document_a_name'] as String,
      documentBName: json['document_b_name'] as String,
      overallSimilarityPercent:
          (json['overall_similarity_percent'] as num).toDouble(),
      riskLevel: RiskLevel.values.firstWhere(
        (e) => e.name == json['risk_level'] || (e == RiskLevel.veryHigh && json['risk_level'] == 'very_high'),
        orElse: () {
          final percent = (json['overall_similarity_percent'] as num).toDouble();
          if (percent <= 25) return RiskLevel.low;
          if (percent <= 50) return RiskLevel.medium;
          if (percent <= 75) return RiskLevel.high;
          return RiskLevel.veryHigh;
        },
      ),
      matchedSections: (json['matched_sections'] as List<dynamic>)
          .map((e) => MatchedSentencePair.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendation: json['recommendation'] as String,
      checkedAt: DateTime.parse(json['checked_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'document_a_name': documentAName,
        'document_b_name': documentBName,
        'overall_similarity_percent': overallSimilarityPercent,
        'risk_level': riskLevel.name,
        'matched_sections': matchedSections.map((e) => e.toJson()).toList(),
        'recommendation': recommendation,
        'checked_at': checkedAt.toIso8601String(),
      };
}
