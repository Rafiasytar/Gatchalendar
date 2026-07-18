package com.example.gachalendar.data

import com.example.gachalendar.model.EventType
import com.example.gachalendar.model.Game
import com.example.gachalendar.model.GameEvent
import java.time.LocalDateTime

object DummyData {
    val games = listOf(
        Game(id = "gi", name = "Genshin Impact", developer = "Hoyoverse"),
        Game(id = "hsr", name = "Honkai: Star Rail", developer = "Hoyoverse"),
        Game(id = "zzz", name = "Zenless Zone Zero", developer = "Hoyoverse"),
        Game(id = "wuwa", name = "Wuthering Waves", developer = "Kuro Games"),
        Game(id = "ark", name = "Arknights", developer = "Hypergryph")
    )

    val events = listOf(
        // Genshin Impact Events
        GameEvent(
            id = "gi_banner_1",
            gameId = "gi",
            title = "Character Banner: Venti & Neuvillette",
            description = "Boosted drop rate for Venti and Neuvillette",
            startTime = LocalDateTime.now().minusDays(2),
            endTime = LocalDateTime.now().plusDays(14),
            type = EventType.BANNER
        ),
        GameEvent(
            id = "gi_event_1",
            gameId = "gi",
            title = "Lantern Rite Festival",
            description = "Annual Liyue festival with minigames and rewards.",
            startTime = LocalDateTime.now().plusDays(1),
            endTime = LocalDateTime.now().plusDays(20),
            type = EventType.IN_GAME_EVENT
        ),

        // Honkai Star Rail Events
        GameEvent(
            id = "hsr_banner_1",
            gameId = "hsr",
            title = "Character Banner: Acheron",
            description = "Boosted drop rate for Acheron",
            startTime = LocalDateTime.now().minusDays(5),
            endTime = LocalDateTime.now().plusDays(10),
            type = EventType.BANNER
        ),
        GameEvent(
            id = "hsr_event_1",
            gameId = "hsr",
            title = "Cosmic Coin Collection",
            description = "Collect coins in simulated universe.",
            startTime = LocalDateTime.now().minusDays(1),
            endTime = LocalDateTime.now().plusDays(5),
            type = EventType.IN_GAME_EVENT
        ),

        // Wuthering Waves Events
        GameEvent(
            id = "wuwa_banner_1",
            gameId = "wuwa",
            title = "Resonator Convene: Yinlin",
            description = "Featured resonator Yinlin",
            startTime = LocalDateTime.now().plusDays(3),
            endTime = LocalDateTime.now().plusDays(24),
            type = EventType.BANNER
        )
    )
}
