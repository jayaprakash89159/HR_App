import 'dart:io';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';

import 'api_service.dart';

class AttendanceService extends ChangeNotifier {
  final ApiService _api;

  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _todayAttendance;
  List<Map<String, dynamic>> _monthlyRecords = [];

  bool get isLoading => _isLoading;
  String? get error => _error;
  Map<String, dynamic>? get todayAttendance => _todayAttendance;
  List<Map<String, dynamic>> get monthlyRecords => _monthlyRecords;

  bool get isClockedIn => _todayAttendance?['clock_in'] != null;
  bool get isClockedOut => _todayAttendance?['clock_out'] != null;

  AttendanceService(this._api);

  // ===== Location =====
  Future<Position?> getCurrentLocation() async {
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.deniedForever) return null;

      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );
    } catch (e) {
      return null;
    }
  }

  Future<String> getAddressFromPosition(Position pos) async {
    try {
      final placemarks = await placemarkFromCoordinates(pos.latitude, pos.longitude);
      if (placemarks.isNotEmpty) {
        final p = placemarks.first;
        return [p.street, p.subLocality, p.locality, p.postalCode]
            .where((s) => s != null && s.isNotEmpty)
            .join(', ');
      }
    } catch (_) {}
    return '${pos.latitude.toStringAsFixed(5)}, ${pos.longitude.toStringAsFixed(5)}';
  }

  // ===== Camera / Selfie =====
  Future<File?> captureSelfie(BuildContext context) async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) return null;

      // Find front camera
      final frontCamera = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );

      final controller = CameraController(frontCamera, ResolutionPreset.medium);
      await controller.initialize();

      File? selfieFile;

      await showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        backgroundColor: Colors.transparent,
        builder: (ctx) => _SelfieCapture(
          controller: controller,
          onCapture: (file) {
            selfieFile = file;
            Navigator.pop(ctx);
          },
          onCancel: () => Navigator.pop(ctx),
        ),
      );

      await controller.dispose();
      return selfieFile;
    } catch (e) {
      return null;
    }
  }

  // ===== Clock In =====
  Future<bool> clockIn(BuildContext context) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Get location
      final position = await getCurrentLocation();
      String address = '';
      if (position != null) {
        address = await getAddressFromPosition(position);
      }

      // Capture selfie
      File? selfie;
      if (context.mounted) {
        selfie = await captureSelfie(context);
      }

      // Prepare fields
      final fields = <String, String>{
        'source': 'mobile',
        if (position != null) 'latitude': position.latitude.toString(),
        if (position != null) 'longitude': position.longitude.toString(),
        if (address.isNotEmpty) 'address': address,
      };

      // Make API call
      final response = await _api.postMultipart(
        '/api/v1/attendance/clock-in/',
        fields,
        imageFile: selfie,
      );

      if (response.success) {
        _todayAttendance = response.data;
        notifyListeners();
        return true;
      } else {
        _error = response.error;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ===== Clock Out =====
  Future<bool> clockOut(BuildContext context) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final position = await getCurrentLocation();
      String address = '';
      if (position != null) {
        address = await getAddressFromPosition(position);
      }

      File? selfie;
      if (context.mounted) {
        selfie = await captureSelfie(context);
      }

      final fields = <String, String>{
        'source': 'mobile',
        if (position != null) 'latitude': position.latitude.toString(),
        if (position != null) 'longitude': position.longitude.toString(),
        if (address.isNotEmpty) 'address': address,
      };

      final response = await _api.postMultipart(
        '/api/v1/attendance/clock-out/',
        fields,
        imageFile: selfie,
      );

      if (response.success) {
        _todayAttendance = {...?_todayAttendance, ...response.data};
        notifyListeners();
        return true;
      } else {
        _error = response.error;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ===== Fetch Today's Attendance =====
  Future<void> fetchTodayAttendance() async {
    final response = await _api.get('/api/v1/attendance/today/');
    if (response.success) {
      _todayAttendance = response.data;
      notifyListeners();
    }
  }

  // ===== Fetch Monthly Records =====
  Future<void> fetchMonthlyRecords({int? year, int? month}) async {
    final now = DateTime.now();
    final y = year ?? now.year;
    final m = month ?? now.month;

    final response = await _api.get('/api/v1/attendance/?date_from=$y-${m.toString().padLeft(2, '0')}-01&date_to=$y-${m.toString().padLeft(2, '0')}-31');
    if (response.success && response.data['results'] != null) {
      _monthlyRecords = List<Map<String, dynamic>>.from(response.data['results']);
      notifyListeners();
    }
  }
}

// ===== Selfie Capture Widget =====
class _SelfieCapture extends StatelessWidget {
  final CameraController controller;
  final Function(File) onCapture;
  final VoidCallback onCancel;

  const _SelfieCapture({
    required this.controller,
    required this.onCapture,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
      decoration: const BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // Handle
          Container(
            margin: const EdgeInsets.only(top: 8),
            width: 40, height: 4,
            decoration: BoxDecoration(
              color: Colors.white24,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          // Title
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text('Take Selfie',
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w700)),
          ),
          // Camera preview
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: CameraPreview(controller),
            ),
          ),
          const SizedBox(height: 16),
          // Capture button
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              TextButton.icon(
                onPressed: onCancel,
                icon: const Icon(Icons.close, color: Colors.white70),
                label: const Text('Skip', style: TextStyle(color: Colors.white70)),
              ),
              GestureDetector(
                onTap: () async {
                  try {
                    final image = await controller.takePicture();
                    onCapture(File(image.path));
                  } catch (_) { onCancel(); }
                },
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white24, width: 4),
                  ),
                  child: const Icon(Icons.camera_alt, size: 30, color: Colors.black),
                ),
              ),
              const SizedBox(width: 80), // Balance
            ],
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
