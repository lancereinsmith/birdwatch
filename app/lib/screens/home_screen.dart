import 'package:flutter/material.dart';

import 'detection_list_screen.dart';

/// Home: entry to detections list and live listen (Phase 3).
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Birdwatch'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            FilledButton.icon(
              onPressed: () => Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => const DetectionListScreen(),
                ),
              ),
              icon: const Icon(Icons.list),
              label: const Text('View detections'),
            ),
            const SizedBox(height: 24),
            const Text(
              'Real-time listen: tap to start (not yet implemented)',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }
}
