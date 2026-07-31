import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/constants/app_colors.dart';
import '../../data/providers/plagiarism_check_provider.dart';
import '../../data/models/risk_level.dart';
import '../report/report_screen.dart';

class ResultsScreen extends StatelessWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final result = context.watch<PlagiarismCheckProvider>().result;

    if (result == null) {
      return const Scaffold(
        body: Center(child: Text('No result available.')),
      );
    }

    final riskColor = AppColors.forRisk(result.riskLevel);

    return Scaffold(
      appBar: AppBar(title: const Text('Results')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    SizedBox(
                      height: 140,
                      width: 140,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          CircularProgressIndicator(
                            value: result.overallSimilarityPercent / 100,
                            strokeWidth: 12,
                            backgroundColor: Colors.grey.shade200,
                            valueColor: AlwaysStoppedAnimation(riskColor),
                          ),
                          Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                '${result.overallSimilarityPercent.toStringAsFixed(0)}%',
                                style: TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: riskColor,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                result.riskLevel.label,
                                style: TextStyle(
                                  color: riskColor,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${result.documentAName}  vs  ${result.documentBName}',
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 8),
                          Text(result.recommendation),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 8,
                            children: [
                              OutlinedButton.icon(
                                onPressed: () {},
                                icon: const Icon(Icons.share),
                                label: const Text('Share'),
                              ),
                              ElevatedButton.icon(
                                onPressed: () => Navigator.of(context).push(
                                  MaterialPageRoute(
                                      builder: (_) => const ReportScreen()),
                                ),
                                icon: const Icon(Icons.report),
                                label: const Text('View Detailed Report'),
                              ),
                            ],
                          )
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: ListView(
                children: result.matchedSections.map((pair) => Card(
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
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w600),
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
                                style:
                                    const TextStyle(color: AppColors.textSecondary)),
                            const SizedBox(height: 4),
                            Text('Doc B: ${pair.textB}',
                                style:
                                    const TextStyle(color: AppColors.textSecondary)),
                          ],
                        ),
                      ),
                    )).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
