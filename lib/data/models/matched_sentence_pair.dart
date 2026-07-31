/// Represents one matched sentence pair between Document A and Document B,
/// as shown in the "Most Similar Sections" part of the report.
class MatchedSentencePair {
  final int sentenceIndexA;
  final int sentenceIndexB;
  final String textA;
  final String textB;
  final double similarityPercent; // 0–100

  MatchedSentencePair({
    required this.sentenceIndexA,
    required this.sentenceIndexB,
    required this.textA,
    required this.textB,
    required this.similarityPercent,
  });

  factory MatchedSentencePair.fromJson(Map<String, dynamic> json) {
    return MatchedSentencePair(
      sentenceIndexA: json['sentence_index_a'] as int,
      sentenceIndexB: json['sentence_index_b'] as int,
      textA: json['text_a'] as String,
      textB: json['text_b'] as String,
      similarityPercent: (json['similarity_percent'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'sentence_index_a': sentenceIndexA,
        'sentence_index_b': sentenceIndexB,
        'text_a': textA,
        'text_b': textB,
        'similarity_percent': similarityPercent,
      };
}
