import 'dart:io';

import '../models/similarity_result_model.dart';

/// Contract for comparing two documents and getting a plagiarism result.
///
/// UI code (screens/widgets) should ONLY ever depend on this interface,
/// never on [MockPlagiarismRepository] or [ApiPlagiarismRepository] directly.
/// That's what makes swapping mock -> real backend a one-line change later.
abstract class PlagiarismRepository {
  /// Uploads Document A and Document B and returns the comparison result.
  Future<SimilarityResultModel> compareDocuments({
    required File documentA,
    required File documentB,
  });
}
