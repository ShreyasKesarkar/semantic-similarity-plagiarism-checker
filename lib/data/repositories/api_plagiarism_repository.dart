import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/similarity_result_model.dart';
import 'plagiarism_repository.dart';

/// Real implementation that talks to the FastAPI backend.
///
/// TODO once backend is ready:
/// 1. Set [baseUrl] to your FastAPI server address.
/// 2. Confirm the endpoint path and field names match your FastAPI response
///    (adjust SimilarityResultModel.fromJson if your backend uses different
///    keys, e.g. camelCase vs snake_case).
/// 3. Swap MockPlagiarismRepository -> ApiPlagiarismRepository in main.dart.
///    No other file needs to change.
class ApiPlagiarismRepository implements PlagiarismRepository {
  final String baseUrl;

  ApiPlagiarismRepository({required this.baseUrl});

  @override
  Future<SimilarityResultModel> compareDocuments({
    required File documentA,
    required File documentB,
  }) async {
    final uri = Uri.parse('$baseUrl/compare');

    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        await http.MultipartFile.fromPath('document_a', documentA.path),
      )
      ..files.add(
        await http.MultipartFile.fromPath('document_b', documentB.path),
      );

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
