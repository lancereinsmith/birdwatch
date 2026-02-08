import 'package:flutter/material.dart';

import '../models/detection.dart';
import '../services/amplify_sync_service.dart';
import 'detection_detail_screen.dart';

/// List of detections (from Pi and local); updates via DataStore stream.
class DetectionListScreen extends StatelessWidget {
  const DetectionListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detections'),
      ),
      body: StreamBuilder<List<Detection>>(
        stream: observeDetections(),
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading detections…'),
                ],
              ),
            );
          }
          final list = snapshot.requireData;
          if (list.isEmpty) {
            return const Center(
              child: Text('No detections yet.\nSync from Pi or listen live.'),
            );
          }
          return ListView.builder(
            itemCount: list.length,
            itemBuilder: (context, index) {
              final detection = list[index];
              return _DetectionTile(
                detection: detection,
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) =>
                        DetectionDetailScreen(detection: detection),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class _DetectionTile extends StatelessWidget {
  const _DetectionTile({
    required this.detection,
    required this.onTap,
  });

  final Detection detection;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final name =
        detection.commonName ?? detection.scientificName ?? detection.speciesCode;
    return ListTile(
      title: Text(name),
      subtitle: Text(
        '${(detection.confidence * 100).toStringAsFixed(0)}% · ${detection.deviceId}',
      ),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}
