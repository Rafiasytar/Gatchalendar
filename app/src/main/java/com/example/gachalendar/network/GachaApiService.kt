package com.example.gachalendar.network

import com.example.gachalendar.model.GameEvent
import com.google.gson.GsonBuilder
import com.google.gson.JsonDeserializer
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

interface GachaApiService {
    @GET("events.json")
    suspend fun getEvents(
        @Query("t") timestamp: Long? = null
    ): List<GameEvent>
}

object RetrofitInstance {
    // Mengarah ke GitHub Pages milik Anda
    private const val BASE_URL = "https://rafiasytar.github.io/Gatchalendar/"

    private val gson = GsonBuilder()
        .registerTypeAdapter(LocalDateTime::class.java, JsonDeserializer { json, _, _ ->
            parseEventTime(json.asString)
        })
        .create()

    /**
     * Waktu event dikirim dengan offset zona waktu server (mis. "2026-11-04T11:00:00+08:00").
     * Konversi ke zona waktu perangkat agar status aktif/berakhir dan countdown akurat.
     * Format lama tanpa offset dianggap waktu server Asia (UTC+8).
     */
    fun parseEventTime(value: String): LocalDateTime {
        val parsed = DateTimeFormatter.ISO_DATE_TIME.parseBest(
            value, OffsetDateTime::from, LocalDateTime::from
        )
        val offsetTime = when (parsed) {
            is OffsetDateTime -> parsed
            else -> (parsed as LocalDateTime).atOffset(ZoneOffset.ofHours(8))
        }
        return offsetTime.atZoneSameInstant(ZoneId.systemDefault()).toLocalDateTime()
    }

    val api: GachaApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(GachaApiService::class.java)
    }
}
