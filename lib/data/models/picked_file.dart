import 'dart:typed_data';

/// Platform-agnostic file wrapper.
/// On native (Android/iOS/Windows), [path] is set.
/// On Flutter Web, [bytes] is set and [path] is null.
class PickedFile {
  final String name;
  final String? path;
  final Uint8List? bytes;

  const PickedFile({
    required this.name,
    this.path,
    this.bytes,
  });

  bool get isValid => path != null || bytes != null;
}
