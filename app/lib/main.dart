import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

// Amplify: add plugins and Amplify.configure(amplifyOutputs) when cloud/ is deployed
// import 'package:amplify_flutter/amplify_flutter.dart';
// import 'package:amplify_auth_cognito/amplify_auth_cognito.dart';
// import 'package:amplify_api/amplify_api.dart';
// import 'package:amplify_datastore/amplify_datastore.dart';
// import 'package:amplify_storage_s3/amplify_storage_s3.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const BirdwatchApp());
}

class BirdwatchApp extends StatelessWidget {
  const BirdwatchApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Birdwatch',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
