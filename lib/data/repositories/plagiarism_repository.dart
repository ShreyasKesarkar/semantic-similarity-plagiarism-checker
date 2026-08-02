import '../models/picked_file.dart';
import '../models/similarity_result_model.dart';

/// Contract for comparing two documents and getting a plagiarism result.
///
/// UI code (screens/widgets) should ONLY ever depend on this interface,
/// never on [MockPlagiarismRepository] or [ApiPlagiarismRepository] directly.
abstract class PlagiarismRepository {
  /// Compares Document A and Document B and returns the comparison result.
  /// Uses [PickedFile] to support both web (bytes) and native (path).
  Future<SimilarityResultModel> compareDocumentsFromPicked({
    required PickedFile documentA,
    required PickedFile documentB,
  });
}
