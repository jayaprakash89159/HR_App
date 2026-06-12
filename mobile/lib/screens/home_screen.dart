import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../services/auth_service.dart';
import '../services/attendance_service.dart';
import '../utils/app_theme.dart';
import '../widgets/stat_card.dart';
import '../widgets/leave_balance_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AttendanceService>().fetchTodayAttendance();
    });
  }

  String get _greeting {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final attendance = context.watch<AttendanceService>();
    final user = auth.currentUser;

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: RefreshIndicator(
        color: AppTheme.primary,
        onRefresh: () => attendance.fetchTodayAttendance(),
        child: CustomScrollView(
          slivers: [
            // App Bar
            SliverAppBar(
              expandedHeight: 140,
              pinned: true,
              backgroundColor: AppTheme.primary,
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color(0xFF1E40AF), Color(0xFF2563EB)],
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Row(
                        children: [
                          CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.white.withOpacity(0.2),
                            child: Text(
                              (user?['first_name'] ?? 'U').substring(0, 1).toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w800,
                                fontSize: 20,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  '$_greeting,',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.8),
                                    fontSize: 13,
                                  ),
                                ),
                                Text(
                                  '${user?['first_name'] ?? 'Employee'} 👋',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 18,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                                Text(
                                  DateFormat('EEEE, dd MMMM yyyy').format(DateTime.now()),
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.7),
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          // Notification bell
                          Stack(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                                onPressed: () {},
                              ),
                              Positioned(
                                right: 8, top: 8,
                                child: Container(
                                  width: 8, height: 8,
                                  decoration: const BoxDecoration(
                                    color: Color(0xFFF59E0B),
                                    shape: BoxShape.circle,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),

            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // ===== Attendance Clock Card =====
                  _AttendanceClockCard(attendance: attendance),
                  const SizedBox(height: 16),

                  // ===== Today's Stats =====
                  _TodayStatsRow(attendance: attendance),
                  const SizedBox(height: 16),

                  // ===== Quick Actions =====
                  _QuickActions(),
                  const SizedBox(height: 16),

                  // ===== Leave Balances =====
                  const LeaveBalanceCard(),
                  const SizedBox(height: 80), // Bottom nav space
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ===== Attendance Clock Card =====
class _AttendanceClockCard extends StatelessWidget {
  final AttendanceService attendance;

  const _AttendanceClockCard({required this.attendance});

  @override
  Widget build(BuildContext context) {
    final clockIn = attendance.todayAttendance?['clock_in'];
    final clockOut = attendance.todayAttendance?['clock_out'];
    final status = attendance.todayAttendance?['status'] ?? 'not_marked';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 20, offset: const Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  StreamBuilder(
                    stream: Stream.periodic(const Duration(seconds: 1)),
                    builder: (ctx, _) {
                      return Text(
                        DateFormat('HH:mm:ss').format(DateTime.now()),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 36,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -1,
                        ),
                      );
                    },
                  ),
                  Text(
                    DateFormat('EEEE, dd MMM').format(DateTime.now()),
                    style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 13),
                  ),
                ],
              ),
              _StatusBadge(status: status),
            ],
          ),

          const SizedBox(height: 16),

          // Clock In/Out times
          Row(
            children: [
              _TimeInfo(label: 'In', time: clockIn != null ? DateFormat('HH:mm').format(DateTime.parse(clockIn)) : '--:--', color: AppTheme.secondary),
              Container(width: 1, height: 32, color: Colors.white12, margin: const EdgeInsets.symmetric(horizontal: 16)),
              _TimeInfo(label: 'Out', time: clockOut != null ? DateFormat('HH:mm').format(DateTime.parse(clockOut)) : '--:--', color: AppTheme.danger),
              Container(width: 1, height: 32, color: Colors.white12, margin: const EdgeInsets.symmetric(horizontal: 16)),
              _TimeInfo(
                label: 'Hours',
                time: attendance.todayAttendance?['working_hours_display'] ?? '0h 0m',
                color: AppTheme.accent,
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Action Buttons
          if (attendance.isLoading)
            const Center(child: CircularProgressIndicator(color: Colors.white))
          else
            Row(
              children: [
                Expanded(
                  child: _ClockButton(
                    label: 'Clock In',
                    icon: Icons.login_rounded,
                    color: AppTheme.secondary,
                    enabled: !attendance.isClockedIn,
                    onTap: () async {
                      final success = await attendance.clockIn(context);
                      if (context.mounted) {
                        _showSnack(context, success ? 'Clocked in successfully! ✅' : (attendance.error ?? 'Failed'), success);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _ClockButton(
                    label: 'Clock Out',
                    icon: Icons.logout_rounded,
                    color: AppTheme.danger,
                    enabled: attendance.isClockedIn && !attendance.isClockedOut,
                    onTap: () async {
                      final confirm = await _confirmClockOut(context);
                      if (confirm == true) {
                        final success = await attendance.clockOut(context);
                        if (context.mounted) {
                          _showSnack(context, success ? 'Clocked out successfully! 👋' : (attendance.error ?? 'Failed'), success);
                        }
                      }
                    },
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Future<bool?> _confirmClockOut(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Clock Out'),
        content: const Text('Are you sure you want to clock out?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Clock Out')),
        ],
      ),
    );
  }

  void _showSnack(BuildContext context, String msg, bool success) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: success ? AppTheme.secondary : AppTheme.danger,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
    ));
  }
}

class _ClockButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final bool enabled;
  final VoidCallback onTap;

  const _ClockButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: enabled ? color : color.withOpacity(0.3),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: enabled ? onTap : null,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: Colors.white, size: 18),
              const SizedBox(width: 8),
              Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 14)),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;

  const _StatusBadge({required this.status});

  Color get _color {
    switch (status) {
      case 'present': case 'late_mark': return AppTheme.secondary;
      case 'absent': return AppTheme.danger;
      case 'half_day': return const Color(0xFF8B5CF6);
      case 'leave': return AppTheme.primary;
      case 'holiday': return AppTheme.accent;
      default: return Colors.grey;
    }
  }

  String get _label {
    switch (status) {
      case 'present': return 'Present';
      case 'late_mark': return 'Late';
      case 'absent': return 'Absent';
      case 'half_day': return 'Half Day';
      case 'leave': return 'On Leave';
      case 'holiday': return 'Holiday';
      default: return 'Not Marked';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _color.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 6, height: 6, decoration: BoxDecoration(color: _color, shape: BoxShape.circle)),
          const SizedBox(width: 6),
          Text(_label, style: TextStyle(color: _color, fontSize: 11, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class _TimeInfo extends StatelessWidget {
  final String label, time;
  final Color color;

  const _TimeInfo({required this.label, required this.time, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10, fontWeight: FontWeight.w700)),
        const SizedBox(height: 2),
        Text(time, style: TextStyle(color: color, fontSize: 14, fontWeight: FontWeight.w700)),
      ],
    );
  }
}

class _TodayStatsRow extends StatelessWidget {
  final AttendanceService attendance;

  const _TodayStatsRow({required this.attendance});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: StatCard(label: 'Working', value: attendance.todayAttendance?['working_hours_display'] ?? '0h', icon: Icons.timer_outlined, color: AppTheme.primary)),
        const SizedBox(width: 10),
        Expanded(child: StatCard(label: 'Overtime', value: '0h', icon: Icons.access_time_filled, color: AppTheme.secondary)),
        const SizedBox(width: 10),
        Expanded(child: StatCard(label: 'Break', value: '${attendance.todayAttendance?['total_break_minutes'] ?? 0}m', icon: Icons.coffee_outlined, color: AppTheme.accent)),
      ],
    );
  }
}

class _QuickActions extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final actions = [
      {'icon': Icons.beach_access_rounded, 'label': 'Apply Leave', 'color': AppTheme.primary, 'route': '/leave/apply'},
      {'icon': Icons.work_outline_rounded, 'label': 'On Duty', 'color': AppTheme.secondary, 'route': '/od/apply'},
      {'icon': Icons.schedule_rounded, 'label': 'Short Leave', 'color': AppTheme.accent, 'route': '/short-leave'},
      {'icon': Icons.receipt_long_rounded, 'label': 'Payslips', 'color': const Color(0xFF8B5CF6), 'route': '/payslips'},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Quick Actions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
        const SizedBox(height: 10),
        Row(
          children: actions.map((action) {
            return Expanded(
              child: GestureDetector(
                onTap: () {}, // Navigate
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppTheme.surface,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Column(
                    children: [
                      Container(
                        width: 40, height: 40,
                        decoration: BoxDecoration(
                          color: (action['color'] as Color).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(action['icon'] as IconData, color: action['color'] as Color, size: 20),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        action['label'] as String,
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: AppTheme.textSecondary),
                        textAlign: TextAlign.center,
                        maxLines: 2,
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}
