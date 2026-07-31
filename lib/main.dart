import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/constants/app_colors.dart';
import 'data/providers/plagiarism_check_provider.dart';
import 'data/repositories/api_plagiarism_repository.dart';
import 'features/upload/upload_screen.dart';

void main() {
  runApp(const PlagiarismCheckerApp());
}

class PlagiarismCheckerApp extends StatelessWidget {
  const PlagiarismCheckerApp({super.key});

  static String get _baseUrl =>
      defaultTargetPlatform == TargetPlatform.android
          ? 'http://10.0.2.2:8000'
          : 'http://127.0.0.1:8000';

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => PlagiarismCheckProvider(
        repository: ApiPlagiarismRepository(baseUrl: _baseUrl),
      ),
      child: MaterialApp(
        title: 'Plagiarism Checker',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          scaffoldBackgroundColor: AppColors.background,
          colorSchemeSeed: AppColors.primary,
          appBarTheme: const AppBarTheme(
            backgroundColor: AppColors.primary,
            elevation: 0,
            centerTitle: true,
            foregroundColor: Colors.white,
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
            ),
          ),
          cardTheme: CardThemeData(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            elevation: 4,
            margin: EdgeInsets.zero,
          ),
        ),
        home: const UploadScreen(),
      ),
    );
  }
}
