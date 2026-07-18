package com.example.gachalendar.model

import java.time.LocalDateTime

data class Game(
    val id: String,
    val name: String,
    val developer: String,
    val imageUrl: String = "" // Placeholder for game icon/cover
)

data class GameEvent(
    val id: String,
    val gameId: String,
    val title: String,
    val description: String,
    val startTime: LocalDateTime,
    val endTime: LocalDateTime,
    val type: EventType
)

enum class EventType {
    BANNER,
    IN_GAME_EVENT,
    LOGIN_EVENT,
    MAINTENANCE,
    OTHER
}
