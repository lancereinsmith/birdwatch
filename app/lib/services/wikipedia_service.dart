/// Wikipedia API: page summary (thumbnail, extract) for scientific name.
library;

import 'package:http/http.dart' as http;

const _base = 'https://en.wikipedia.org/api/rest_v1/page/summary/';

/// Fetches summary for a Wikipedia page title (e.g. scientific name).
Future<WikipediaSummary?> fetchSummary(String pageTitle) async {
  final uri = Uri.parse('$_base${Uri.encodeComponent(pageTitle)}');
  final response = await http.get(uri);
  if (response.statusCode != 200) return null;
  // TODO: parse JSON for thumbnail, extract
  return null;
}

class WikipediaSummary {
  final String? thumbnailUrl;
  final String? extract;
  const WikipediaSummary({this.thumbnailUrl, this.extract});
}
