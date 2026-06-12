import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'api_service.dart';

class AuthService extends ChangeNotifier {
  final ApiService _api;
  final SharedPreferences _prefs;

  Map<String, dynamic>? _currentUser;
  bool _isLoading = false;
  bool _isInitialized = false;

  Map<String, dynamic>? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _currentUser != null;
  bool get isInitialized => _isInitialized;

  AuthService(this._api, this._prefs) {
    _init();
  }

  Future<void> _init() async {
    final userJson = _prefs.getString('current_user');
    if (userJson != null) {
      try {
        _currentUser = jsonDecode(userJson);
      } catch (_) {}
    }
    _isInitialized = true;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _api.post('/api/v1/auth/login/', {
        'email': email,
        'password': password,
      });

      if (response.success) {
        final data = response.data;
        await _api.saveTokens(data['access'], data['refresh']);
        _currentUser = data['user'];
        await _prefs.setString('current_user', jsonEncode(_currentUser));
        notifyListeners();
        return true;
      }
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _api.clearTokens();
    await _prefs.remove('current_user');
    _currentUser = null;
    notifyListeners();
  }

  String get userRole => _currentUser?['role'] ?? 'employee';
  bool get isManager => userRole == 'manager' || userRole == 'hr_admin' || userRole == 'super_admin';
  bool get isHR => userRole == 'hr_admin' || userRole == 'super_admin';
}
