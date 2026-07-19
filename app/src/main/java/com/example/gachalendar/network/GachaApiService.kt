package com.example.gachalendar.network

import com.example.gachalendar.model.GameEvent
import com.google.gson.GsonBuilder
import com.google.gson.JsonDeserializer
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query
import java.time.LocalDateTime
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
            LocalDateTime.parse(json.asString, DateTimeFormatter.ISO_DATE_TIME)
        })
        .create()

    val api: GachaApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(GachaApiService::class.java)
    }
}
