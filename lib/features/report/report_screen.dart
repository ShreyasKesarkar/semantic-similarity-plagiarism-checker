import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/constants/app_colors.dart';
import '../../data/models/risk_level.dart';
import '../../data/providers/plagiarism_check_provider.dart';

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});

  void _downloadReport(BuildContext context) {
    // On web: instruct the user to use Ctrl+P → Save as PDF
    // (dart:html window.print() can be added via conditional imports if needed)
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          kIsWeb
              ? 'Press Ctrl+P (or ⌘+P on Mac), then choose "Save as PDF"'
              : 'PDF export is available when running on web (Chrome).',
        ),
        duration: const Duration(seconds: 5),
        backgroundColor: AppColors.primary,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final result = context.watch<PlagiarismCheckProvider>().result;

    if (result == null) {
      return const Scaffold(
        body: Center(child: Text('No report available.')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Detailed Report'),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            tooltip: 'Download as PDF',
            onPressed: () => _downloadReport(context),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Summary header card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Plagiarism Report',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text('Document A: ${result.documentAName}', style: const TextStyle(color: AppColors.textSecondary)),
                  Text('Document B: ${result.documentBName}', style: const TextStyle(color: AppColors.textSecondary)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Text('Overall Similarity: ', style: TextStyle(fontWeight: FontWeight.w600)),
                      Text(
                        '${result.overallSimilarityPercent.toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: AppColors.forRisk(result.riskLevel),
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.forRisk(result.riskLevel).withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppColors.forRisk(result.riskLevel).withValues(alpha: 0.4)),
                        ),
                        child: Text(
                          result.riskLevel.label,
                          style: TextStyle(
                            color: AppColors.forRisk(result.riskLevel),
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(result.recommendation, style: const TextStyle(color: AppColors.textSecondary)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Most Similar Sections',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 12),
          ...result.matchedSections.map(
            (pair) => Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Sentence ${pair.sentenceIndexA} ↔ ${pair.sentenceIndexB}',
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.forRisk(result.riskLevel).withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${pair.similarityPercent.toStringAsFixed(0)}%',
                            style: TextStyle(
                              color: AppColors.forRisk(result.riskLevel),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Document A', style: TextStyle(fontSize: 11, color: AppColors.textSecondary, fontWeight: FontWeight.w600)),
                          const SizedBox(height: 2),
                          Text(pair.textA, style: const TextStyle(color: AppColors.textPrimary)),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Document B', style: TextStyle(fontSize: 11, color: AppColors.textSecondary, fontWeight: FontWeight.w600)),
                          const SizedBox(height: 2),
                          Text(pair.textB, style: const TextStyle(color: AppColors.textPrimary)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => _downloadReport(context),
            icon: const Icon(Icons.download),
            label: const Text('Download Report (Save as PDF)'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
