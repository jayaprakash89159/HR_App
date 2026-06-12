// attendance_screen.dart
import 'package:flutter/material.dart';
import '../utils/app_theme.dart';

class AttendanceScreen extends StatelessWidget {
  const AttendanceScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('My Attendance')),
    body: const Center(child: Text('Attendance records coming soon')),
  );
}
