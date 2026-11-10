package com.example.gachalendar.notification

import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import com.example.gachalendar.model.GameEvent
import com.example.gachalendar.receiver.EventReminderReceiver
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.temporal.ChronoUnit

object EventNotificationManager {

    private const val TAG = "EventNotification"
    private const val PREFS = "event_reminders"
    private const val KEY_SCHEDULED = "scheduled_request_codes"

    /**
     * Android membatasi maksimal 500 alarm per aplikasi (melewatinya = crash).
     * Kita hanya memasang pengingat terdekat; sisanya dipasang ulang setiap aplikasi dibuka.
     */
    private const val MAX_SCHEDULED_ALARMS = 60

    private val milestones = listOf(
        Milestone(ChronoUnit.DAYS, 3, "3 Hari"),
        Milestone(ChronoUnit.DAYS, 2, "2 Hari"),
        Milestone(ChronoUnit.DAYS, 1, "1 Hari"),
        Milestone(ChronoUnit.HOURS, 12, "12 Jam"),
        Milestone(ChronoUnit.HOURS, 6, "6 Jam"),
        Milestone(ChronoUnit.HOURS, 3, "3 Jam"),
        Milestone(ChronoUnit.HOURS, 1, "1 Jam")
    )

    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Pengingat Event"
            val descriptionText = "Notifikasi pengingat event gacha yang hampir selesai"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel("event_reminders", name, importance).apply {
                description = descriptionText
            }
            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    fun scheduleRemindersForEvents(context: Context, events: List<GameEvent>) {
        try {
            scheduleInternal(context.applicationContext, events)
        } catch (e: Exception) {
            // Pengingat bersifat tambahan: jangan pernah membuat aplikasi crash
            Log.e(TAG, "Gagal menjadwalkan pengingat", e)
        }
    }

    private fun scheduleInternal(context: Context, events: List<GameEvent>) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val now = LocalDateTime.now()

        // Kumpulkan semua pengingat yang masih di masa depan, lalu ambil yang paling dekat
        val reminders = events
            .filter { it.endTime.isAfter(now) }
            .flatMap { event ->
                milestones.mapIndexedNotNull { index, milestone ->
                    val trigger = event.endTime.minus(milestone.value, milestone.unit)
                    // Lewati yang sudah lewat atau sebelum event dimulai
                    if (trigger.isAfter(now) && !trigger.isBefore(event.startTime)) {
                        Reminder(event, milestone, (event.id.hashCode() * 31) + index, trigger)
                    } else null
                }
            }
            .sortedBy { it.triggerTime }
            .distinctBy { it.requestCode }
            .take(MAX_SCHEDULED_ALARMS)

        // Batalkan alarm lama yang tidak lagi termasuk daftar terbaru
        val newCodes = reminders.map { it.requestCode }.toSet()
        val oldCodes = prefs.getStringSet(KEY_SCHEDULED, emptySet())!!
            .mapNotNull { it.toIntOrNull() }
        oldCodes.filterNot { it in newCodes }.forEach { code ->
            PendingIntent.getBroadcast(
                context, code, Intent(context, EventReminderReceiver::class.java),
                PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
            )?.let {
                alarmManager.cancel(it)
                it.cancel()
            }
        }

        val scheduled = mutableSetOf<String>()
        for (reminder in reminders) {
            val intent = Intent(context, EventReminderReceiver::class.java).apply {
                putExtra("event_id", reminder.event.id)
                putExtra("event_title", reminder.event.title)
                putExtra("game_id", reminder.event.gameId)
                putExtra("milestone_desc", reminder.milestone.description)
            }
            val pendingIntent = PendingIntent.getBroadcast(
                context,
                reminder.requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            val alarmTimeMs = reminder.triggerTime.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()

            try {
                setAlarm(alarmManager, alarmTimeMs, pendingIntent)
                scheduled.add(reminder.requestCode.toString())
            } catch (e: Exception) {
                // Mis. batas alarm sistem tercapai: hentikan, tapi jangan crash
                Log.w(TAG, "Berhenti menjadwalkan setelah ${scheduled.size} alarm", e)
                break
            }
        }

        prefs.edit().putStringSet(KEY_SCHEDULED, scheduled).apply()
    }

    private fun setAlarm(alarmManager: AlarmManager, timeMs: Long, pendingIntent: PendingIntent) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !alarmManager.canScheduleExactAlarms()) {
                alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, timeMs, pendingIntent)
            } else {
                alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, timeMs, pendingIntent)
            }
        } catch (e: SecurityException) {
            // Izin exact alarm dicabut: pakai alarm tidak presisi
            alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, timeMs, pendingIntent)
        }
    }

    private data class Milestone(
        val unit: ChronoUnit,
        val value: Long,
        val description: String
    )

    private data class Reminder(
        val event: GameEvent,
        val milestone: Milestone,
        val requestCode: Int,
        val triggerTime: LocalDateTime
    )
}
