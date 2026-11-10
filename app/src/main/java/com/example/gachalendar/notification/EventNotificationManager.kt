package com.example.gachalendar.notification

import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import com.example.gachalendar.model.GameEvent
import com.example.gachalendar.receiver.EventReminderReceiver
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.temporal.ChronoUnit

object EventNotificationManager {

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
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val now = LocalDateTime.now()

        events.forEach { event ->
            // Only schedule if the event's end time is in the future
            if (event.endTime.isAfter(now)) {
                val endDateTime = event.endTime

                // Define our target milestones: duration to subtract, and the text description
                val milestones = listOf(
                    Milestone(ChronoUnit.DAYS, 3, "3 Hari"),
                    Milestone(ChronoUnit.DAYS, 2, "2 Hari"),
                    Milestone(ChronoUnit.DAYS, 1, "1 Hari"),
                    Milestone(ChronoUnit.HOURS, 12, "12 Jam"),
                    Milestone(ChronoUnit.HOURS, 6, "6 Jam"),
                    Milestone(ChronoUnit.HOURS, 3, "3 Jam"),
                    Milestone(ChronoUnit.HOURS, 1, "1 Jam")
                )

                milestones.forEachIndexed { index, milestone ->
                    val triggerTime = endDateTime.minus(milestone.value, milestone.unit)

                    // Only schedule if the calculated alarm trigger time is in the future
                    if (triggerTime.isAfter(now)) {
                        val alarmTimeMs = triggerTime.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()

                        val intent = Intent(context, EventReminderReceiver::class.java).apply {
                            putExtra("event_id", event.id)
                            putExtra("event_title", event.title)
                            putExtra("game_id", event.gameId)
                            putExtra("milestone_desc", milestone.description)
                        }

                        // Generate unique request code to avoid collision
                        val requestCode = (event.id.hashCode() * 31) + index

                        val pendingIntent = PendingIntent.getBroadcast(
                            context,
                            requestCode,
                            intent,
                            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                        )

                        // Schedule alarm with safety checks for Android 12+ API 31+ exact alarm permission
                        try {
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                                if (alarmManager.canScheduleExactAlarms()) {
                                    alarmManager.setExactAndAllowWhileIdle(
                                        AlarmManager.RTC_WAKEUP,
                                        alarmTimeMs,
                                        pendingIntent
                                    )
                                } else {
                                    alarmManager.setAndAllowWhileIdle(
                                        AlarmManager.RTC_WAKEUP,
                                        alarmTimeMs,
                                        pendingIntent
                                    )
                                }
                            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                alarmManager.setExactAndAllowWhileIdle(
                                    AlarmManager.RTC_WAKEUP,
                                    alarmTimeMs,
                                    pendingIntent
                                )
                            } else {
                                alarmManager.set(
                                    AlarmManager.RTC_WAKEUP,
                                    alarmTimeMs,
                                    pendingIntent
                                )
                            }
                        } catch (e: SecurityException) {
                            // Fallback to inexact alarm if security exception occurs
                            alarmManager.set(
                                AlarmManager.RTC_WAKEUP,
                                alarmTimeMs,
                                pendingIntent
                            )
                        }
                    }
                }
            }
        }
    }

    private data class Milestone(
        val unit: ChronoUnit,
        val value: Long,
        val description: String
    )
}
