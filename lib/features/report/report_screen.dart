import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/constants/app_colors.dart';
import '../../data/providers/plagiarism_check_provider.dart';

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final result = context.watch<PlagiarismCheckProvider>().result;

    if (result == null) {
      return const Scaffold(
        body: Center(child: Text('No report available.')),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Detailed Report')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'Most Similar Sections',
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
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
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.forRisk(result.riskLevel)
                                .withValues(alpha: 0.12),
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
                    Text('Doc A: ${pair.textA}',
                        style: const TextStyle(color: AppColors.textSecondary)),
                    const SizedBox(height: 4),
                    Text('Doc B: ${pair.textB}',
                        style: const TextStyle(color: AppColors.textSecondary)),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    // TODO: implement PDF download/export once backend report
                    // generation endpoint is ready.
                  },
                  icon: const Icon(Icons.download),
                  label: const Text('Download Report'),
                ),
              ),
              const SizedBox(width: 12),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.cast_for_education),
                label: const Text('Start Review'),
              )
            ],
          ),
        ],
      ),
    );
  }
}
