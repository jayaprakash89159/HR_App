// profile_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../utils/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final user = auth.currentUser;

    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Center(
            child: Column(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: AppTheme.primary,
                  child: Text(
                    (user?['first_name'] ?? 'U').substring(0, 1).toUpperCase(),
                    style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.w800),
                  ),
                ),
                const SizedBox(height: 12),
                Text('${user?['first_name'] ?? ''} ${user?['last_name'] ?? ''}',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                Text(user?['email'] ?? '', style: const TextStyle(color: AppTheme.textMuted, fontSize: 14)),
              ],
            ),
          ),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.logout_rounded, color: AppTheme.danger),
            title: const Text('Sign Out', style: TextStyle(color: AppTheme.danger, fontWeight: FontWeight.w600)),
            onTap: () => auth.logout(),
          ),
        ],
      ),
    );
  }
}
