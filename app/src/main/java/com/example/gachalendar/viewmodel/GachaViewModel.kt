package com.example.gachalendar.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.gachalendar.data.DummyData
import com.example.gachalendar.model.Game
import com.example.gachalendar.model.GameEvent
import com.example.gachalendar.network.RetrofitInstance
import com.example.gachalendar.notification.EventNotificationManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class GachaViewModel(application: Application) : AndroidViewModel(application) {

    private val _games = MutableStateFlow<List<Game>>(DummyData.games)
    val games: StateFlow<List<Game>> = _games

    private val _events = MutableStateFlow<List<GameEvent>>(emptyList())
    val events: StateFlow<List<GameEvent>> = _events

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage

    init {
        fetchEvents()
    }

    private var lastFetchMs = 0L

    fun refreshEvents() {
        fetchEvents()
    }

    /** Dipanggil setiap aplikasi kembali ke foreground; hindari fetch berulang dalam 1 menit. */
    fun refreshIfStale() {
        if (System.currentTimeMillis() - lastFetchMs > 60_000L && !_isLoading.value) {
            fetchEvents()
        }
    }

    private fun fetchEvents() {
        lastFetchMs = System.currentTimeMillis()
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // Selalu pakai cache-buster agar tidak mendapat events.json lama dari cache CDN
                val fetchedEvents = RetrofitInstance.api.getEvents(System.currentTimeMillis())
                _events.value = fetchedEvents
                _errorMessage.value = null
                EventNotificationManager.scheduleRemindersForEvents(getApplication(), fetchedEvents)
            } catch (e: Exception) {
                // If API fails, fallback to DummyData for now so the app doesn't break
                if (_events.value.isEmpty()) {
                    _events.value = DummyData.events
                }
                _errorMessage.value = "Failed to fetch from server, using local data."
                EventNotificationManager.scheduleRemindersForEvents(getApplication(), _events.value)
            } finally {
                _isLoading.value = false
            }
        }
    }
}
