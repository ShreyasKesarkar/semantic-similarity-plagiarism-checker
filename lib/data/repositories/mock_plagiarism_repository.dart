import 'dart:io';
import 'dart:math';

import '../models/matched_sentence_pair.dart';
import '../models/risk_level.dart';
import '../models/similarity_result_model.dart';
import 'plagiarism_repository.dart';

/// Mock implementation used while the FastAPI backend isn't built yet.
/// Simulates network delay and returns a realistic fake result so every
/// screen (loading -> results -> report) can be built and demoed today.
class MockPlagiarismRepository implements PlagiarismRepository {
  @override
  Future<SimilarityResultModel> compareDocuments({
    required File documentA,
    required File documentB,
  }) async {
    // Simulate processing time (text extraction + SBERT embedding + cosine sim).
    await Future.delayed(const Duration(seconds: 2));

    const overallSimilarity = 87.0;

    return SimilarityResultModel(
      id: 'mock-${Random().nextInt(99999)}',
      documentAName: documentA.path.split('/').last,
      documentBName: documentB.path.split('/').last,
      overallSimilarityPercent: overallSimilarity,
      riskLevel: _riskFromPercent(overallSimilarity),
      matchedSections: [
        MatchedSentencePair(
          sentenceIndexA: 14,
          sentenceIndexB: 22,
          textA:
              'The mitochondria is the powerhouse of the cell, responsible for generating ATP.',
          textB:
              'Mitochondria act as the cell\'s powerhouse, producing ATP for energy.',
          similarityPercent: 94.0,
        ),
        MatchedSentencePair(
          sentenceIndexA: 31,
          sentenceIndexB: 18,
          textA:
              'Climate change has accelerated due to increased greenhouse gas emissions.',
          textB:
              'Greenhouse gas emissions have sped up the pace of climate change.',
          similarityPercent: 91.0,
        ),
        MatchedSentencePair(
          sentenceIndexA: 45,
          sentenceIndexB: 52,
          textA:
              'Machine learning models require large datasets to generalize well.',
          textB:
              'Large datasets are necessary for machine learning models to generalize effectively.',
          similarityPercent: 89.0,
        ),
      ],
      recommendation:
          'This document contains highly similar content. Manual review of '
          'highlighted sections is recommended before making a final '
          'plagiarism determination.',
      checkedAt: DateTime.now(),
    );
  }

  RiskLevel _riskFromPercent(double percent) {
    if (percent < 30) return RiskLevel.low;
    if (percent < 60) return RiskLevel.medium;
    return RiskLevel.high;
  }
}
