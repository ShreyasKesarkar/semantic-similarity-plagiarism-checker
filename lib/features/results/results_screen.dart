import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/constants/app_colors.dart';
import '../../data/providers/plagiarism_check_provider.dart';
import '../../data/models/risk_level.dart';
import '../../core/utils/ai_explanation_generator.dart';
import '../report/report_screen.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({super.key});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> with SingleTickerProviderStateMixin {
  late AnimationController _staggerController;

  @override
  void initState() {
    super.initState();
    _staggerController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );
    _staggerController.forward();
  }

  @override
  void dispose() {
    _staggerController.dispose();
    super.dispose();
  }

  RiskLevel _riskForScore(double percent) {
    if (percent <= 25) return RiskLevel.low;
    if (percent <= 50) return RiskLevel.medium;
    if (percent <= 75) return RiskLevel.high;
    return RiskLevel.veryHigh;
  }

  @override
  Widget build(BuildContext context) {
    final result = context.watch<PlagiarismCheckProvider>().result;

    if (result == null) {
      return const Scaffold(
        body: Center(child: Text('No result available.')),
      );
    }

    final riskColor = AppColors.forRisk(result.riskLevel);
    final explanation = AiExplanationGenerator.generateExplanation(
        result.riskLevel, result.overallSimilarityPercent);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Results')),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          children: [
            // General Stats and Risk Badge
            AnimatedBuilder(
              animation: _staggerController,
              builder: (context, child) {
                final val = CurvedAnimation(
                  parent: _staggerController,
                  curve: const Interval(0.0, 0.4, curve: Curves.easeOut),
                ).value;
                return Transform.translate(
                  offset: Offset(0, 20 * (1 - val)),
                  child: Opacity(opacity: val, child: child),
                );
              },
              child: Card(
                elevation: 4,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
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
                            TweenAnimationBuilder<double>(
                              tween: Tween<double>(
                                  begin: 0, end: result.overallSimilarityPercent / 100),
                              duration: const Duration(milliseconds: 1200),
                              curve: Curves.easeOutCubic,
                              builder: (context, value, child) {
                                return SizedBox(
                                  height: 140,
                                  width: 140,
                                  child: CircularProgressIndicator(
                                    value: value,
                                    strokeWidth: 12,
                                    backgroundColor: Colors.grey.shade200,
                                    valueColor: AlwaysStoppedAnimation(riskColor),
                                  ),
                                );
                              },
                            ),
                            TweenAnimationBuilder<double>(
                              tween: Tween<double>(
                                  begin: 0, end: result.overallSimilarityPercent),
                              duration: const Duration(milliseconds: 1200),
                              curve: Curves.easeOutCubic,
                              builder: (context, value, child) {
                                return Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      '${value.toStringAsFixed(0)}%',
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
                                      textAlign: TextAlign.center,
                                    ),
                                  ],
                                );
                              }
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
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                            ),
                            const SizedBox(height: 8),
                            // Improved Risk Badge
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              decoration: BoxDecoration(
                                color: riskColor.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: riskColor.withValues(alpha: 0.3)),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.shield_rounded, color: riskColor, size: 20),
                                  const SizedBox(width: 8),
                                  Text(
                                    result.riskLevel.label,
                                    style: TextStyle(
                                      color: riskColor,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
                            // AI Similarity Explanation
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade50,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.blue.shade200),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(Icons.auto_awesome, color: Colors.blue.shade700, size: 16),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      explanation,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.blue.shade900,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
                            Wrap(
                              spacing: 8,
                              children: [
                                OutlinedButton.icon(
                                  onPressed: () {},
                                  icon: const Icon(Icons.share, size: 18),
                                  label: const Text('Share'),
                                ),
                                ElevatedButton.icon(
                                  onPressed: () => Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const ReportScreen()),
                                  ),
                                  icon: const Icon(Icons.report, size: 18),
                                  label: const Text('Report'),
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
            ),
            const SizedBox(height: 24),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Matched Sentences',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: result.matchedSections.length,
                itemBuilder: (context, index) {
                  final pair = result.matchedSections[index];
                  final sentenceRisk = _riskForScore(pair.similarityPercent);
                  final sentenceColor = AppColors.forRisk(sentenceRisk);

                  // Stagger computation
                  final start = 0.3 + (index * 0.1).clamp(0.0, 0.6);
                  final end = (start + 0.3).clamp(0.0, 1.0);

                  return AnimatedBuilder(
                    animation: _staggerController,
                    builder: (context, child) {
                      final val = CurvedAnimation(
                        parent: _staggerController,
                        curve: Interval(start, end, curve: Curves.easeOut),
                      ).value;
                      return Transform.translate(
                        offset: Offset(50 * (1 - val), 0),
                        child: Opacity(opacity: val, child: child),
                      );
                    },
                    child: Card(
                      elevation: 2,
                      margin: const EdgeInsets.only(bottom: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'Match #${index + 1}',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: sentenceColor.withValues(alpha: 0.12),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(color: sentenceColor.withValues(alpha: 0.5)),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.compare_arrows, size: 14, color: sentenceColor),
                                      const SizedBox(width: 4),
                                      Text(
                                        '${pair.similarityPercent.toStringAsFixed(0)}% Similar',
                                        style: TextStyle(
                                          color: sentenceColor,
                                          fontWeight: FontWeight.w700,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            _buildSentenceBox('Document A (Sentence ${pair.sentenceIndexA})', pair.textA, sentenceColor),
                            const SizedBox(height: 8),
                            _buildSentenceBox('Document B (Sentence ${pair.sentenceIndexB})', pair.textB, sentenceColor),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSentenceBox(String title, String text, Color color) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 4),
          Text(
            text,
            style: const TextStyle(fontSize: 14, color: AppColors.textPrimary, height: 1.4),
          ),
        ],
      ),
    );
  }
}
