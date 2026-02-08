/// eBird API 2.0: recent observations in a region (for spatial validation).
///
/// Reduces false positives: if species not in recent list for user's region,
/// flag as "Unlikely" or suppress.
library;

import 'package:http/http.dart' as http;

const _base = 'https://api.ebird.org/v2';

/// Recent observations in region (e.g. US-CA-037). Requires X-eBirdApiToken.
Future<List<String>> recentSpeciesInRegion(String regionCode, String apiKey) async {
  final uri = Uri.parse('$_base/data/obs/$regionCode/recent');
  final response = await http.get(
    uri,
    headers: {'X-eBirdApiToken': apiKey},
  );
  if (response.statusCode != 200) return [];
  // TODO: parse JSON and return list of species codes
  return [];
}

/// Reverse geocode lat/lon to eBird region code (e.g. county).
Future<String?> regionCodeForLatLon(double lat, double lon) async {
  // TODO: use a geocoding API or static grid to get region code
  return null;
}
