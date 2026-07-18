package com.example.gachalendar.network

import com.example.gachalendar.model.GameEvent
import com.google.gson.GsonBuilder
import com.google.gson.JsonDeserializer
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

interface GachaApiService {
    @GET("events.json")
    suspend fun getEvents(): List<GameEvent>
}

object RetrofitInstance {
    // TODO: Ganti URL ini dengan URL GitHub Pages Anda nanti (misalnya: https://username.github.io/Gachalendar/)
    private const val BASE_URL = "https://raw.githubusercontent.com/username/Gachalendar/main/"

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
