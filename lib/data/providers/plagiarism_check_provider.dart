import 'package:flutter/foundation.dart';

import '../models/picked_file.dart';
import '../models/similarity_result_model.dart';
import '../repositories/plagiarism_repository.dart';

enum CheckStatus { idle, uploading, analyzing, success, error }

/// Holds the state for the whole "compare two documents" flow:
/// file selection -> analysis -> result.
///
/// Uses [PickedFile] instead of dart:io File to work on both web and native.
class PlagiarismCheckProvider extends ChangeNotifier {
  final PlagiarismRepository _repository;

  PlagiarismCheckProvider({required PlagiarismRepository repository})
      : _repository = repository;

  PickedFile? documentA;
  PickedFile? documentB;
  CheckStatus status = CheckStatus.idle;
  SimilarityResultModel? result;
  String? errorMessage;

  bool get canRunCheck => documentA != null && documentB != null;

  void setDocumentA(PickedFile file) {
    documentA = file;
    notifyListeners();
  }

  void setDocumentB(PickedFile file) {
    documentB = file;
    notifyListeners();
  }

  Future<void> runCheck() async {
    if (!canRunCheck) return;

    status = CheckStatus.analyzing;
    errorMessage = null;
    notifyListeners();

    try {
      result = await _repository.compareDocumentsFromPicked(
        documentA: documentA!,
        documentB: documentB!,
      );
      status = CheckStatus.success;
    } catch (e) {
      status = CheckStatus.error;
      errorMessage = e.toString();
    }
    notifyListeners();
  }

  void reset() {
    documentA = null;
    documentB = null;
    status = CheckStatus.idle;
    result = null;
    errorMessage = null;
    notifyListeners();
  }
}
