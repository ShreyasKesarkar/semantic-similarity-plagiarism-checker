# Plagiarism Checker — Frontend Scaffold

## What's in here
A working Flutter flow: **Upload → Analyzing → Results → Report**, fully wired
to a `Provider` + repository pattern, currently running on **mock data**
(`MockPlagiarismRepository`) since the FastAPI backend isn't built yet.

## How to drop this into your project
1. Copy the `lib/` folder into your existing Flutter project (merge with your
   current `lib/`, don't overwrite `main.dart` if you've already customized it).
2. Add the dependencies from `pubspec_additions.yaml` to your real `pubspec.yaml`.
3. Run `flutter pub get`.
4. Run the app — you should be able to pick two PDF/DOCX files, tap
   "Run Plagiarism Check", and see a mock 87% similarity result with matched
   sentence pairs.

## The key idea: swapping mock for real backend later
Everything in `features/` talks to `PlagiarismCheckProvider`, which talks to
a `PlagiarismRepository` **interface** — never directly to mock or API code.

When your FastAPI backend is ready:
1. Open `lib/main.dart`
2. Change this one line:
   ```dart
   repository: MockPlagiarismRepository(),
   ```
   to:
   ```dart
   repository: ApiPlagiarismRepository(baseUrl: 'http://your-backend-url'),
   ```
3. That's it — no screen, widget, or provider code needs to change.

`ApiPlagiarismRepository` (in `data/repositories/api_plagiarism_repository.dart`)
already has the multipart upload logic stubbed — you'll just need to confirm
the endpoint path (`/compare`) and JSON field names match what FastAPI
actually returns, and adjust `SimilarityResultModel.fromJson` if needed.

## Using this with GitHub Copilot
Good prompts to feed Copilot file-by-file:
- In `upload_screen.dart`: "Add drag-and-drop support for web" or
  "Add file size validation, reject files over 10MB"
- In `results_screen.dart`: "Animate the circular gauge filling on screen load"
- In `report_screen.dart`: "Highlight the differing words between textA and
  textB using a diff algorithm"
- New file `features/dashboard/dashboard_screen.dart`: "Build a dashboard
  screen showing a list of past checks using SimilarityResultModel, with
  risk-colored badges, sorted by checkedAt descending"

Because the models and repository contract are already defined, Copilot will
autocomplete against real types instead of guessing — that's the main payoff
of scaffolding this first.

## Folder structure
```
lib/
├── main.dart                     # swap point: mock vs real repository
├── core/constants/app_colors.dart
├── data/
│   ├── models/                   # SimilarityResultModel, MatchedSentencePair, RiskLevel
│   ├── repositories/             # interface + mock + (stub) API impl
│   └── providers/                # PlagiarismCheckProvider (Provider/ChangeNotifier)
└── features/
    ├── upload/upload_screen.dart
    ├── results/results_screen.dart
    └── report/report_screen.dart
```

## Not built yet (left for you / Copilot)
- Dashboard screen (history of past checks)
- Drag-and-drop file zone styling
- PDF report download/export
- Loading/analyzing screen with step-by-step progress (currently just a
  spinner on the button)
- Light input validation messaging (wrong file type, etc. — file_picker
  already restricts to pdf/docx via `allowedExtensions`)
