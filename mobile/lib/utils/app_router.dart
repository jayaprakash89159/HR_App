import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/auth_service.dart';
import '../screens/home_screen.dart';
import '../screens/login_screen.dart';
import '../screens/attendance_screen.dart';
import '../screens/leave_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/payslip_screen.dart';
import '../widgets/main_shell.dart';

class AppRouter {
  static GoRouter router(AuthService auth) {
    return GoRouter(
      initialLocation: '/',
      redirect: (context, state) {
        final isLoggedIn = auth.isAuthenticated;
        final isLoginPage = state.matchedLocation == '/login';
        if (!isLoggedIn && !isLoginPage) return '/login';
        if (isLoggedIn && isLoginPage) return '/';
        return null;
      },
      refreshListenable: auth,
      routes: [
        GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
        ShellRoute(
          builder: (context, state, child) => MainShell(child: child),
          routes: [
            GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
            GoRoute(path: '/attendance', builder: (_, __) => const AttendanceScreen()),
            GoRoute(path: '/leave', builder: (_, __) => const LeaveScreen()),
            GoRoute(path: '/payslips', builder: (_, __) => const PayslipScreen()),
            GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
          ],
        ),
      ],
    );
  }
}
