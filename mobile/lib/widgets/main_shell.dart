import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../utils/app_theme.dart';

class MainShell extends StatelessWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  int _currentIndex(BuildContext context) {
    final loc = GoRouterState.of(context).matchedLocation;
    if (loc == '/') return 0;
    if (loc.startsWith('/attendance')) return 1;
    if (loc.startsWith('/leave')) return 2;
    if (loc.startsWith('/payslips')) return 3;
    if (loc.startsWith('/profile')) return 4;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppTheme.surface,
          border: Border(top: BorderSide(color: AppTheme.border)),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -2))],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex(context),
          onTap: (i) {
            switch (i) {
              case 0: context.go('/'); break;
              case 1: context.go('/attendance'); break;
              case 2: context.go('/leave'); break;
              case 3: context.go('/payslips'); break;
              case 4: context.go('/profile'); break;
            }
          },
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.grid_view_rounded), label: 'Home'),
            BottomNavigationBarItem(icon: Icon(Icons.fingerprint_rounded), label: 'Attendance'),
            BottomNavigationBarItem(icon: Icon(Icons.beach_access_rounded), label: 'Leave'),
            BottomNavigationBarItem(icon: Icon(Icons.receipt_long_rounded), label: 'Payslips'),
            BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Profile'),
          ],
        ),
      ),
    );
  }
}
