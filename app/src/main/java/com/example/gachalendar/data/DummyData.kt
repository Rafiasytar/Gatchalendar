package com.example.gachalendar.data

import com.example.gachalendar.model.EventType
import com.example.gachalendar.model.Game
import com.example.gachalendar.model.GameEvent
import java.time.LocalDateTime

object DummyData {
    val games = listOf(
        Game(id = "gi", name = "Genshin Impact", developer = "Hoyoverse", imageUrl = "https://play-lh.googleusercontent.com/YQqyKaXX-63krqsfIzUEJWUWLINxcb5tbS6QVySdxbS7eZV7YB2dUjUvX27xA0TIGtfxQ5v-tQjwlT5tTB-O=w240-h480"),
        Game(id = "hsr", name = "Honkai: Star Rail", developer = "Hoyoverse", imageUrl = "https://play-lh.googleusercontent.com/aWrGocSA7hEuk1qAPe7L4T57LvLKrwwH26cK2_LOqxRQMQX7j3uHYojC-EKWgYEV2PdrmE0ahqvvhLhXrAGk6Q=w240-h480"),
        Game(id = "zzz", name = "Zenless Zone Zero", developer = "Hoyoverse", imageUrl = "https://play-lh.googleusercontent.com/-ZZaqZBQ7EBjH4j0hyHX-0Fu0jUtnoOc-LwydvgQmsXWBZLxyAhxPcmIakzZB7NFurlK4Mj0pbvYe0pHYSuv4p8=w240-h480"),
        Game(id = "wuwa", name = "Wuthering Waves", developer = "Kuro Games", imageUrl = "https://play-lh.googleusercontent.com/f8SoRHdK3E8ofPV6ZbXG-TkcNtXiGmgXnPLl_zjHh6OsSQ1yZqbDIDWFI2P7UCnAQGY_C9VUv2Q8P87CIAqH=w240-h480"),
        Game(id = "endfield", name = "Arknights Endfield", developer = "Hypergryph", imageUrl = "https://play-lh.googleusercontent.com/l6FVNa293RykBWy88TqEhUakIcGSC8bRygSnKOBgztln48JX-WzMWnrBAETrKZsxDNC4HhwCsvfle_UI7rBE"),
        Game(id = "nte", name = "Neverness to Everness", developer = "Hotta Studio", imageUrl = "https://play-lh.googleusercontent.com/TGl3DdDbi4hty6ooOhEvv_2s5tkpGLbL6derP8y5hK-_Bw--Ve375b08ba9HHQ9ueRpoQ9oye1T_T24BJriLUmw"),
        Game(id = "p5x", name = "Persona 5: The Phantom X", developer = "Perfect World Games", imageUrl = "https://play-lh.googleusercontent.com/ILTvSTvGulNfs6FUQJeeYdB-dbS9Eo7LDkJ2wjM-jFrpamWgEhdVKhJ752Yn8wyEgmEoVd3nDFd9Dncf_RzKGA")
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
        ),

        // Neverness to Everness Events
        GameEvent(
            id = "nte_event_1",
            gameId = "nte",
            title = "Pre-registration Rewards",
            description = "Claim pre-registration milestone rewards.",
            startTime = LocalDateTime.now().minusDays(1),
            endTime = LocalDateTime.now().plusDays(30),
            type = EventType.IN_GAME_EVENT
        ),

        // Persona 5: The Phantom X Events
        GameEvent(
            id = "p5x_banner_1",
            gameId = "p5x",
            title = "Character Banner: Joker",
            description = "Featured Phantom Thief Joker",
            startTime = LocalDateTime.now().minusDays(3),
            endTime = LocalDateTime.now().plusDays(15),
            type = EventType.BANNER
        )
    )
}
