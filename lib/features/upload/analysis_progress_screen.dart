import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../data/providers/plagiarism_check_provider.dart';
import '../results/results_screen.dart';

class AnalysisProgressScreen extends StatefulWidget {
  const AnalysisProgressScreen({super.key});

  @override
  State<AnalysisProgressScreen> createState() => _AnalysisProgressScreenState();
}

class _AnalysisProgressScreenState extends State<AnalysisProgressScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  final List<String> _steps = [
    'Uploading Documents',
    'Extracting Text',
    'Cleaning Text',
    'Generating Embeddings',
    'Comparing Documents',
    'Generating Report',
  ];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    );

    // Defer until after the first frame to avoid notifyListeners() during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startProcess();
    });
  }

  Future<void> _startProcess() async {
    final provider = context.read<PlagiarismCheckProvider>();
    
    // Start backend process and animation in parallel
    final results = await Future.wait([
      provider.runCheck(),
      _controller.forward(),
    ]);

    if (!mounted) return;

    if (provider.status == CheckStatus.success) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const ResultsScreen()),
      );
    } else {
      // If error, pop back to show error on upload screen
      Navigator.of(context).pop();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'Analyzing Documents...',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              const Text(
                'Please wait while we process your documents and perform a deep semantic comparison.',
                style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              ...List.generate(_steps.length, (index) {
                final start = index / _steps.length;
                final end = (index + 1) / _steps.length;
                final animation = CurvedAnimation(
                  parent: _controller,
                  curve: Interval(start, end, curve: Curves.easeIn),
                );

                return AnimatedBuilder(
                  animation: _controller,
                  builder: (context, child) {
                    final progress = animation.value;
                    final isActive = _controller.value >= start;
                    final isDone = _controller.value >= end;

                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12.0),
                      child: Row(
                        children: [
                          Container(
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: isDone
                                  ? AppColors.primary
                                  : (isActive ? AppColors.primary.withValues(alpha: 0.2) : Colors.grey.shade300),
                              border: Border.all(
                                color: isDone ? AppColors.primary : (isActive ? AppColors.primary : Colors.grey.shade400),
                                width: 2,
                              ),
                            ),
                            child: isDone
                                ? const Icon(Icons.check, size: 16, color: Colors.white)
                                : (isActive
                                    ? Padding(
                                        padding: const EdgeInsets.all(4.0),
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                                        ),
                                      )
                                    : null),
                          ),
                          const SizedBox(width: 16),
                          Text(
                            _steps[index],
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: isDone || isActive ? FontWeight.w600 : FontWeight.w400,
                              color: isDone ? AppColors.textPrimary : (isActive ? AppColors.primary : Colors.grey),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                );
              }),
            ],
          ),
        ),
      ),
    );
  }
}
