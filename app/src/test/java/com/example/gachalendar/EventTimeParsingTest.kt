package com.example.gachalendar

import com.example.gachalendar.network.RetrofitInstance
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import java.time.LocalDateTime
import java.util.TimeZone

class EventTimeParsingTest {
    private lateinit var original: TimeZone

    @Before
    fun setUp() {
        original = TimeZone.getDefault()
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Jakarta")) // UTC+7
    }

    @After
    fun tearDown() {
        TimeZone.setDefault(original)
    }

    @Test
    fun offsetTimeIsConvertedToDeviceZone() {
        // 11:00 UTC+8 == 10:00 WIB
        assertEquals(
            LocalDateTime.of(2026, 11, 4, 10, 0),
            RetrofitInstance.parseEventTime("2026-11-04T11:00:00+08:00")
        )
    }

    @Test
    fun legacyTimeWithoutOffsetIsTreatedAsUtc8() {
        assertEquals(
            LocalDateTime.of(2026, 11, 4, 10, 0),
            RetrofitInstance.parseEventTime("2026-11-04T11:00:00")
        )
    }
}
