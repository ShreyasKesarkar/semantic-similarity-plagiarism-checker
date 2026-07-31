import 'dart:io';

import 'package:flutter/foundation.dart';

import '../models/similarity_result_model.dart';
import '../repositories/plagiarism_repository.dart';

enum CheckStatus { idle, uploading, analyzing, success, error }

/// Holds the state for the whole "compare two documents" flow:
/// file selection -> analysis -> result.
///
/// Screens call methods here; they never talk to the repository directly.
class PlagiarismCheckProvider extends ChangeNotifier {
  final PlagiarismRepository _repository;

  PlagiarismCheckProvider({required PlagiarismRepository repository})
      : _repository = repository;

  File? documentA;
  File? documentB;
  CheckStatus status = CheckStatus.idle;
  SimilarityResultModel? result;
  String? errorMessage;

  bool get canRunCheck => documentA != null && documentB != null;

  void setDocumentA(File file) {
    documentA = file;
    notifyListeners();
  }

  void setDocumentB(File file) {
    documentB = file;
    notifyListeners();
  }

  Future<void> runCheck() async {
    if (!canRunCheck) return;

    status = CheckStatus.analyzing;
    errorMessage = null;
    notifyListeners();

    try {
      result = await _repository.compareDocuments(
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
