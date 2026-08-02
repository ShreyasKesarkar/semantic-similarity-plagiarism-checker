import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/picked_file.dart';
import '../models/similarity_result_model.dart';
import 'plagiarism_repository.dart';

/// Real implementation that talks to the FastAPI backend.
///
/// TODO once backend is ready:
/// 1. Set [baseUrl] to your FastAPI server address.
/// 2. Confirm the endpoint path and field names match your FastAPI response.
/// 3. Swap MockPlagiarismRepository -> ApiPlagiarismRepository in main.dart.
class ApiPlagiarismRepository implements PlagiarismRepository {
  final String baseUrl;

  ApiPlagiarismRepository({required this.baseUrl});

  @override
  Future<SimilarityResultModel> compareDocumentsFromPicked({
    required PickedFile documentA,
    required PickedFile documentB,
  }) async {
    final uri = Uri.parse('$baseUrl/compare');

    final request = http.MultipartRequest('POST', uri);

    if (documentA.bytes != null) {
      request.files.add(http.MultipartFile.fromBytes(
        'document_a', documentA.bytes!,
        filename: documentA.name,
      ));
    } else if (documentA.path != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'document_a', documentA.path!,
      ));
    }

    if (documentB.bytes != null) {
      request.files.add(http.MultipartFile.fromBytes(
        'document_b', documentB.bytes!,
        filename: documentB.name,
      ));
    } else if (documentB.path != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'document_b', documentB.path!,
      ));
    }

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception(
        'Failed to compare documents (status ${response.statusCode}): '
        '${response.body}',
      );
    }

    final json = jsonDecode(response.body) as Map<String, dynamic>;
    return SimilarityResultModel.fromJson(json);
  }
}
