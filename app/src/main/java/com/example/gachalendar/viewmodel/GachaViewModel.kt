package com.example.gachalendar.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.gachalendar.data.DummyData
import com.example.gachalendar.model.Game
import com.example.gachalendar.model.GameEvent
import com.example.gachalendar.network.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class GachaViewModel : ViewModel() {

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

    fun refreshEvents() {
        fetchEvents(isForceRefresh = true)
    }

    private fun fetchEvents(isForceRefresh: Boolean = false) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // Fetch data from API
                val fetchedEvents = if (isForceRefresh) {
                    RetrofitInstance.api.getEvents(System.currentTimeMillis())
                } else {
                    RetrofitInstance.api.getEvents()
                }
                _events.value = fetchedEvents
                _errorMessage.value = null
            } catch (e: Exception) {
                // If API fails, fallback to DummyData for now so the app doesn't break
                if (_events.value.isEmpty()) {
                    _events.value = DummyData.events
                }
                _errorMessage.value = "Failed to fetch from server, using local data."
            } finally {
                _isLoading.value = false
            }
        }
    }
}
