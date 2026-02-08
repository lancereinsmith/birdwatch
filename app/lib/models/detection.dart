/// Detection model (matches Amplify schema).
class Detection {
  const Detection({
    required this.id,
    required this.deviceId,
    required this.speciesCode,
    this.scientificName,
    this.commonName,
    required this.confidence,
    required this.timestamp,
    this.audioUrl,
    this.imageUrl,
  });

  final String id;
  final String deviceId;
  final String speciesCode;
  final String? scientificName;
  final String? commonName;
  final double confidence;
  final DateTime timestamp;
  final String? audioUrl;
  final String? imageUrl;
}
