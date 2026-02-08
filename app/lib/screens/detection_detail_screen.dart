import 'package:flutter/material.dart';

import '../models/detection.dart';

/// Detail view for a single detection (species, confidence, device, links).
class DetectionDetailScreen extends StatelessWidget {
  const DetectionDetailScreen({super.key, required this.detection});

  final Detection detection;

  @override
  Widget build(BuildContext context) {
    final name = detection.commonName ??
        detection.scientificName ??
        detection.speciesCode;
    return Scaffold(
      appBar: AppBar(
        title: Text(name),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _Section(
            title: 'Species',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (detection.commonName != null)
                  Text(
                    detection.commonName!,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                if (detection.scientificName != null)
                  Text(
                    detection.scientificName!,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontStyle: FontStyle.italic,
                        ),
                  ),
                Text('Code: ${detection.speciesCode}'),
              ],
            ),
          ),
          const SizedBox(height: 24),
          _Section(
            title: 'Confidence',
            child: Text(
              '${(detection.confidence * 100).toStringAsFixed(1)}%',
            ),
          ),
          const SizedBox(height: 24),
          _Section(
            title: 'Device',
            child: Text(detection.deviceId),
          ),
          const SizedBox(height: 24),
          _Section(
            title: 'Time',
            child: Text(detection.timestamp.toIso8601String()),
          ),
          if (detection.audioUrl != null) ...[
            const SizedBox(height: 24),
            _Section(
              title: 'Audio',
              child: const Text('Clip available (play not yet implemented).'),
            ),
          ],
          if (detection.imageUrl != null) ...[
            const SizedBox(height: 24),
            _Section(
              title: 'Image',
              child: const Text('Image URL available (load not yet implemented).'),
            ),
          ],
        ],
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                color: Theme.of(context).colorScheme.primary,
              ),
        ),
        const SizedBox(height: 8),
        child,
      ],
    );
  }
}
