package com.example.gachalendar.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.runtime.produceState
import kotlinx.coroutines.delay
import java.time.LocalDateTime

/**
 * Waktu "sekarang" yang terus diperbarui, sehingga event yang baru mulai / baru berakhir
 * langsung berpindah status tanpa perlu restart aplikasi.
 */
@Composable
fun rememberCurrentTime(intervalMs: Long = 30_000L): State<LocalDateTime> =
    produceState(initialValue = LocalDateTime.now()) {
        while (true) {
            delay(intervalMs)
            value = LocalDateTime.now()
        }
    }
