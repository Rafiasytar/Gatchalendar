package com.example.gachalendar.receiver

import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat
import com.example.gachalendar.MainActivity
import com.example.gachalendar.R

class EventReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val eventId = intent.getStringExtra("event_id") ?: return
        val eventTitle = intent.getStringExtra("event_title") ?: "Event Gacha"
        val gameId = intent.getStringExtra("game_id") ?: ""
        val milestoneDesc = intent.getStringExtra("milestone_desc") ?: "berakhir sebentar lagi"

        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Create launch intent when notification is clicked
        val launchIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            eventId.hashCode(),
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // Construct game display name
        val gameName = when (gameId) {
            "gi" -> "Genshin Impact"
            "hsr" -> "Honkai: Star Rail"
            "zzz" -> "Zenless Zone Zero"
            "wuwa" -> "Wuthering Waves"
            "endfield" -> "Arknights: Endfield"
            "nte" -> "Neverness to Everness"
            "p5x" -> "Persona 5: The Phantom X"
            else -> "Game Favoritmu"
        }

        val notification = NotificationCompat.Builder(context, "event_reminders")
            .setSmallIcon(R.drawable.ic_logo) // Use Stelle calendar logo as notification icon
            .setContentTitle("Pengingat Event Gachalendar")
            .setContentText("[$gameName] Event '$eventTitle' akan berakhir dalam $milestoneDesc!")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText("[$gameName] Event '$eventTitle' akan berakhir dalam $milestoneDesc. Segera selesaikan sebelum event ditutup!")
            )
            .build()

        // Show notification with unique ID based on event and milestone to avoid overriding
        val uniqueNotificationId = (eventId.hashCode() * 31) + milestoneDesc.hashCode()
        notificationManager.notify(uniqueNotificationId, notification)
    }
}
