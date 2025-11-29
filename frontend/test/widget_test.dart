// This is a basic Flutter widget test.

import 'package:flutter_test/flutter_test.dart';

import 'package:artifact_scanner/main.dart';

void main() {
  testWidgets('App starts with home screen', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ArtifactScannerApp());

    // Verify that home screen title exists
    expect(find.text('ماسح القطع الأثرية'), findsOneWidget);

    // Verify that camera button exists
    expect(find.text('التقاط صورة'), findsOneWidget);

    // Verify that gallery button exists
    expect(find.text('اختيار من المعرض'), findsOneWidget);
  });
}
