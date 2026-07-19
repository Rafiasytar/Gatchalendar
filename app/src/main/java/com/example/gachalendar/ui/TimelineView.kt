package com.example.gachalendar.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.gachalendar.model.GameEvent
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@Composable
fun TimelineView(
    events: List<GameEvent>,
    onEventClick: (GameEvent) -> Unit,
    modifier: Modifier = Modifier
) {
    val dayWidth = 64.dp
    val laneHeight = 60.dp
    val headerHeight = 80.dp

    // Define timeline range (from 7 days ago to 23 days in the future, total 31 days)
    val today = remember { LocalDate.now() }
    val startGridDate = remember { today.minusDays(7) }
    val endGridDate = remember { today.plusDays(23) }

    val totalDays = remember(startGridDate, endGridDate) {
        ChronoUnit.DAYS.between(startGridDate, endGridDate).toInt() + 1
    }

    val dates = remember(startGridDate, totalDays) {
        (0 until totalDays).map { startGridDate.plusDays(it.toLong()) }
    }

    // Filter events visible in our grid range
    val visibleEvents = remember(events, startGridDate, endGridDate) {
        events.filter {
            val eventStart = it.startTime.toLocalDate()
            val eventEnd = it.endTime.toLocalDate()
            !eventEnd.isBefore(startGridDate) && !eventStart.isAfter(endGridDate)
        }
    }

    // Packing algorithm to group events into non-overlapping horizontal lanes
    val lanes = remember(visibleEvents) {
        val sorted = visibleEvents.sortedBy { it.startTime }
        val result = mutableListOf<MutableList<GameEvent>>()
        for (event in sorted) {
            var placed = false
            for (lane in result) {
                val lastEvent = lane.lastOrNull()
                if (lastEvent != null) {
                    val lastEnd = lastEvent.endTime.toLocalDate()
                    val eventStart = event.startTime.toLocalDate()
                    // Allow placing in the same lane if they don't overlap
                    if (!eventStart.isBefore(lastEnd.plusDays(1))) {
                        lane.add(event)
                        placed = true
                        break
                    }
                }
            }
            if (!placed) {
                result.add(mutableListOf(event))
            }
        }
        result
    }

    val horizontalScrollState = rememberScrollState()
    val verticalScrollState = rememberScrollState()

    // Main horizontal scroll container
    Box(
        modifier = modifier
            .fillMaxSize()
            .horizontalScroll(horizontalScrollState)
    ) {
        // Background Grid Lines (static vertically)
        Row(modifier = Modifier.fillMaxHeight()) {
            dates.forEach { date ->
                val isToday = date == today
                Box(
                    modifier = Modifier
                        .width(dayWidth)
                        .fillMaxHeight()
                        .background(
                            if (isToday) Color.White.copy(alpha = 0.05f)
                            else Color.Transparent
                        )
                ) {
                    // Vertical divider line
                    Box(
                        modifier = Modifier
                            .fillMaxHeight()
                            .width(1.dp)
                            .background(
                                if (isToday) Color.White.copy(alpha = 0.3f)
                                else Color.White.copy(alpha = 0.08f)
                            )
                            .align(Alignment.CenterStart)
                    )
                }
            }
        }

        // Today Vertical Indicator Line
        val todayIndex = dates.indexOf(today)
        if (todayIndex != -1) {
            val todayOffset = (todayIndex * 64).dp
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .width(2.dp)
                    .offset(x = todayOffset)
                    .background(Color.Red.copy(alpha = 0.6f))
            )
        }

        // Content: Sticky Day Header at top, Vertically scrollable Lanes below
        Column(
            modifier = Modifier
                .width((totalDays * 64).dp)
                .fillMaxHeight()
        ) {
            // 1. Header Row (Months & Days) - Fixed at the top of the column
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(headerHeight)
                    .background(Color.Black.copy(alpha = 0.3f))
            ) {
                dates.forEach { date ->
                    val isToday = date == today
                    val dayFormatter = DateTimeFormatter.ofPattern("d")
                    val dayNameFormatter = DateTimeFormatter.ofPattern("E")
                    val monthFormatter = DateTimeFormatter.ofPattern("MMM")

                    Column(
                        modifier = Modifier
                            .width(dayWidth)
                            .fillMaxHeight()
                            .padding(vertical = 6.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Top
                    ) {
                        // Month label
                        if (date == startGridDate || date.dayOfMonth == 1) {
                            Text(
                                text = date.format(monthFormatter),
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = Color.White,
                                fontSize = 10.sp
                            )
                        } else {
                            Text(
                                text = "",
                                fontSize = 10.sp
                            )
                        }

                        Spacer(modifier = Modifier.height(4.dp))

                        // Day Number
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = if (isToday) Color(0xFF3F51B5) else Color.Transparent,
                            contentColor = Color.White
                        ) {
                            Text(
                                text = date.format(dayFormatter),
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                fontSize = 14.sp
                            )
                        }

                        Spacer(modifier = Modifier.height(2.dp))

                        // Day of Week
                        Text(
                            text = date.format(dayNameFormatter),
                            style = MaterialTheme.typography.bodySmall,
                            color = if (isToday) Color.White else Color.White.copy(alpha = 0.6f),
                            fontSize = 11.sp
                        )
                    }
                }
            }

            // Separator line
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(1.dp)
                    .background(Color.White.copy(alpha = 0.15f))
            )

            // 2. Event Lanes Row - Vertically Scrollable
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .verticalScroll(verticalScrollState)
                    .padding(vertical = 12.dp)
            ) {
                if (lanes.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("Tidak ada event aktif di kategori ini.", color = Color.White.copy(alpha = 0.5f))
                    }
                } else {
                    lanes.forEach { lane ->
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(laneHeight),
                            contentAlignment = Alignment.CenterStart
                        ) {
                            lane.forEach { event ->
                                val eventStart = event.startTime.toLocalDate()
                                val eventEnd = event.endTime.toLocalDate()

                                val displayStart = if (eventStart.isBefore(startGridDate)) startGridDate else eventStart
                                val displayEnd = if (eventEnd.isAfter(endGridDate)) endGridDate else eventEnd

                                val startOffsetDays = ChronoUnit.DAYS.between(startGridDate, displayStart)
                                val durationDays = ChronoUnit.DAYS.between(displayStart, displayEnd) + 1

                                val startOffsetDp = (startOffsetDays * 64).toInt().dp
                                val widthDp = (durationDays * 64 - 4).toInt().dp // Subtract 4dp for padding between cards

                                Surface(
                                    modifier = Modifier
                                        .offset(x = startOffsetDp)
                                        .width(widthDp)
                                        .height(44.dp)
                                        .clip(RoundedCornerShape(22.dp))
                                        .clickable { onEventClick(event) },
                                    shape = RoundedCornerShape(22.dp),
                                    color = Color.Transparent,
                                    tonalElevation = 4.dp
                                ) {
                                    val gradientColors = remember(event.gameId) { getGameGradientColors(event.gameId) }
                                    Box(
                                        modifier = Modifier
                                            .fillMaxSize()
                                            .background(
                                                Brush.horizontalGradient(
                                                    colors = listOf(
                                                        gradientColors[0],
                                                        gradientColors[1]
                                                    )
                                                )
                                            )
                                    ) {
                                        // 1. Full Background Image aligned and faded on the right (60% width max)
                                        if (event.imageUrl != null) {
                                            Box(
                                                modifier = Modifier
                                                    .fillMaxHeight()
                                                    .fillMaxWidth(0.6f)
                                                    .align(Alignment.CenterEnd)
                                            ) {
                                                AsyncImage(
                                                    model = event.imageUrl,
                                                    contentDescription = null,
                                                    contentScale = ContentScale.Crop,
                                                    alignment = Alignment.CenterEnd,
                                                    modifier = Modifier.fillMaxSize()
                                                )
                                                // Smooth fade to left
                                                Box(
                                                    modifier = Modifier
                                                        .fillMaxSize()
                                                        .background(
                                                            Brush.horizontalGradient(
                                                                colors = listOf(
                                                                    gradientColors[0],
                                                                    Color.Transparent
                                                                )
                                                            )
                                                        )
                                                )
                                            }
                                        }

                                        // 2. Left accent bar
                                        Box(
                                            modifier = Modifier
                                                .fillMaxHeight()
                                                .width(5.dp)
                                                .background(Color.White.copy(alpha = 0.5f))
                                        )

                                        // 3. Content Text and Mini Thumbnail
                                        Row(
                                            modifier = Modifier
                                                .fillMaxSize()
                                                .padding(start = 12.dp, end = 4.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text(
                                                text = event.title,
                                                style = MaterialTheme.typography.bodyMedium,
                                                fontWeight = FontWeight.ExtraBold,
                                                color = Color.White,
                                                maxLines = 1,
                                                overflow = TextOverflow.Ellipsis,
                                                modifier = Modifier.weight(1f)
                                            )

                                            if (event.imageUrl != null) {
                                                AsyncImage(
                                                    model = event.imageUrl,
                                                    contentDescription = null,
                                                    contentScale = ContentScale.Crop,
                                                    modifier = Modifier
                                                        .size(36.dp)
                                                        .clip(RoundedCornerShape(18.dp))
                                                        .background(Color.White.copy(alpha = 0.2f))
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun getGameGradientColors(gameId: String): List<Color> {
    return when (gameId.lowercase()) {
        "gi", "genshin" -> listOf(Color(0xFF1A365D), Color(0xFF0F1E36)) // Deep blue
        "hsr" -> listOf(Color(0xFF3B1E5F), Color(0xFF201035)) // Cosmic Purple
        "wuwa" -> listOf(Color(0xFF232323), Color(0xFF141414)) // Dark grey
        "zzz" -> listOf(Color(0xFF0A2E1C), Color(0xFF04120B)) // Neon dark green
        "endfield" -> listOf(Color(0xFF6B3000), Color(0xFF381A00)) // Deep industrial orange
        "nte" -> listOf(Color(0xFF0B4E5B), Color(0xFF052A30)) // Cyber Teal
        "p5x" -> listOf(Color(0xFF6B0B0B), Color(0xFF3B0505)) // Crimson red
        else -> listOf(Color(0xFF2E2E2E), Color(0xFF1A1A1A))
    }
}
