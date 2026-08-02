import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/constants/app_colors.dart';
import '../../data/models/picked_file.dart';
import '../../data/providers/plagiarism_check_provider.dart';
import 'analysis_progress_screen.dart';

/// MVP upload screen: teacher selects Document A and Document B,
/// then runs the check. Wired to PlagiarismCheckProvider, which currently
/// uses MockPlagiarismRepository (see main.dart for the swap point).
class UploadScreen extends StatelessWidget {
  const UploadScreen({super.key});

  Future<void> _pickFile(BuildContext context, bool isDocumentA) async {
    final provider = context.read<PlagiarismCheckProvider>();
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx'],
      withData: true, // ensures bytes are loaded on web
    );
    if (result == null || result.files.isEmpty) return;

    final picked = result.files.single;
    final pickedFile = PickedFile(
      name: picked.name,
      path: kIsWeb ? null : picked.path, // NEVER access .path on web — it throws
      bytes: picked.bytes,               // non-null on web after withData: true
    );

    if (!pickedFile.isValid) return;

    if (isDocumentA) {
      provider.setDocumentA(pickedFile);
    } else {
      provider.setDocumentB(pickedFile);
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Plagiarism Checker')),
      body: Consumer<PlagiarismCheckProvider>(
        builder: (context, provider, _) {
          final isAnalyzing = provider.status == CheckStatus.analyzing;

          return Container(
            padding: const EdgeInsets.all(24.0),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0xFFF8FAFC), Colors.white],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Compare two academic documents',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Upload two files (PDF or DOCX) to detect semantic similarity and paraphrased content.',
                  style: TextStyle(color: AppColors.textSecondary),
                ),
                const SizedBox(height: 24),
                _DocumentTile(
                  label: 'Document A',
                  file: provider.documentA,
                  onTap: () => _pickFile(context, true),
                ),
                const SizedBox(height: 16),
                _DocumentTile(
                  label: 'Document B',
                  file: provider.documentB,
                  onTap: () => _pickFile(context, false),
                ),
                const SizedBox(height: 28),
                if (provider.status == CheckStatus.error)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Text(
                      provider.errorMessage ?? 'Something went wrong.',
                      style: const TextStyle(color: AppColors.riskHigh),
                    ),
                  ),
                ElevatedButton(
                  onPressed: provider.canRunCheck && !isAnalyzing
                      ? () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => const AnalysisProgressScreen(),
                            ),
                          );
                        }
                      : null,
                  child: const Text('Run Plagiarism Check'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _DocumentTile extends StatelessWidget {
  final String label;
  final PickedFile? file;
  final VoidCallback onTap;

  const _DocumentTile({
    required this.label,
    required this.file,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final displayName = file?.name;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.cardBackground,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: displayName != null ? AppColors.primary : Colors.grey.shade300,
          ),
        ),
        child: Row(
          children: [
            Icon(
              displayName != null
                  ? Icons.description
                  : Icons.upload_file_outlined,
              color: displayName != null ? AppColors.primary : Colors.grey,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  Text(
                    displayName ?? 'Tap to select PDF or DOCX',
                    style: const TextStyle(fontWeight: FontWeight.w500),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

