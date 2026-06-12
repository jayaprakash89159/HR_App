// payslip_screen.dart
import 'package:flutter/material.dart';
class PayslipScreen extends StatelessWidget {
  const PayslipScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('My Payslips')),
    body: const Center(child: Text('Payslips')),
  );
}
