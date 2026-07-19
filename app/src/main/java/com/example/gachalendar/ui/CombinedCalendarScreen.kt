package com.example.gachalendar.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.gachalendar.model.GameEvent
import com.example.gachalendar.model.EventType
import java.time.LocalDateTime
import java.time.temporal.ChronoUnit
import coil.compose.AsyncImage
import androidx.compose.ui.layout.ContentScale
import androidx.compose.foundation.clickable
import androidx.compose.foundation.background
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.Alignment
import androidx.compose.runtime.remember
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay
import androidx.compose.ui.unit.sp
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.foundation.shape.RoundedCornerShape

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CombinedCalendarScreen(
    events: List<GameEvent>,
    onBackClick: () -> Unit,
    onEventClick: (GameEvent) -> Unit,
    onRefresh: () -> Unit
) {
    // Sort events by end time (closest to ending first)
    val activeEvents = events
        .filter { it.endTime.isAfter(LocalDateTime.now()) }
        .sortedBy { it.endTime }

    var isTimelineView by remember { mutableStateOf(false) }
    var selectedTab by remember { mutableStateOf(0) }

    val filteredActiveEvents = remember(activeEvents, selectedTab) {
        activeEvents.filter { event ->
            when (selectedTab) {
                0 -> event.type == EventType.BANNER
                1 -> event.type == EventType.IN_GAME_EVENT || event.type == EventType.LOGIN_EVENT || event.type == EventType.MAINTENANCE || event.type == EventType.OTHER
                2 -> event.type == EventType.ENDGAME
                else -> true
            }
        }
    }

    val filteredAllEvents = remember(events, selectedTab) {
        events.filter { event ->
            when (selectedTab) {
                0 -> event.type == EventType.BANNER
                1 -> event.type == EventType.IN_GAME_EVENT || event.type == EventType.LOGIN_EVENT || event.type == EventType.MAINTENANCE || event.type == EventType.OTHER
                2 -> event.type == EventType.ENDGAME
                else -> true
            }
        }
    }

    val cosmicGradient = listOf(Color(0xFF0F172A), Color(0xFF070B14))

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        cosmicGradient[0],
                        cosmicGradient[1],
                        Color(0xFF020408)
                    )
                )
            )
    ) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                TopAppBar(
                    title = { Text("Kalender Gabungan", fontWeight = FontWeight.Bold, color = Color.White) },
                    navigationIcon = {
                        IconButton(onClick = onBackClick) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = Color.White
                            )
                        }
                    },
                    actions = {
                        IconButton(onClick = onRefresh) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "Refresh",
                                tint = Color.White
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = Color.White
                    )
                )
            },
            floatingActionButton = {
                ExtendedFloatingActionButton(
                    onClick = { isTimelineView = !isTimelineView },
                    containerColor = Color(0xFF3F51B5),
                    contentColor = Color.White,
                    shape = RoundedCornerShape(24.dp),
                    elevation = FloatingActionButtonDefaults.elevation(defaultElevation = 8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.padding(horizontal = 4.dp)
                    ) {
                        Icon(
                            imageVector = if (isTimelineView) Icons.Default.List else Icons.Default.DateRange,
                            contentDescription = null,
                            tint = Color.White
                        )
                        Text(if (isTimelineView) "List View" else "Timeline View", fontWeight = FontWeight.Bold)
                    }
                }
            }
        ) { paddingValues ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                // Custom Capsule Tab Bar
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                        .background(Color(0x11FFFFFF), RoundedCornerShape(24.dp))
                        .padding(4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    val tabTitles = listOf("Banner Rate Up", "Event Terbatas", "Konten Endgame")
                    tabTitles.forEachIndexed { index, title ->
                        val isSelected = selectedTab == index
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .height(38.dp)
                                .background(
                                    if (isSelected) Color(0xFF3F51B5) else Color.Transparent,
                                    RoundedCornerShape(20.dp)
                                )
                                .clickable { selectedTab = index },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = title,
                                color = if (isSelected) Color.White else Color.White.copy(alpha = 0.6f),
                                fontWeight = FontWeight.Bold,
                                fontSize = 12.sp
                            )
                        }
                    }
                }

                Box(modifier = Modifier.weight(1f)) {
                    if (isTimelineView) {
                        TimelineView(
                            events = filteredAllEvents,
                            onEventClick = onEventClick,
                            modifier = Modifier.fillMaxSize()
                        )
                    } else {
                        LazyColumn(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(horizontal = 16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                            contentPadding = PaddingValues(bottom = 80.dp, top = 8.dp)
                        ) {
                            if (filteredActiveEvents.isEmpty()) {
                                item {
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(top = 40.dp),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            "Tidak ada event aktif di kategori ini saat ini.",
                                            color = Color.White.copy(alpha = 0.6f),
                                            fontWeight = FontWeight.Medium,
                                            fontSize = 14.sp
                                        )
                                    }
                                }
                            } else {
                                items(filteredActiveEvents) { event ->
                                    EventCard(
                                        event = event,
                                        onClick = { onEventClick(event) }
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

@Composable
fun EventCard(event: GameEvent, onClick: () -> Unit = {}) {
    var currentTime by remember { mutableStateOf(LocalDateTime.now()) }
    
    LaunchedEffect(Unit) {
        while (true) {
            delay(1000L)
            currentTime = LocalDateTime.now()
        }
    }

    val totalSeconds = ChronoUnit.SECONDS.between(currentTime, event.endTime)

    val timeLeftText = if (totalSeconds > 0) {
        val daysLeft = totalSeconds / (24 * 3600)
        val hoursLeft = (totalSeconds % (24 * 3600)) / 3600
        val minutesLeft = (totalSeconds % 3600) / 60
        val secondsLeft = totalSeconds % 60

        if (daysLeft > 0) {
            "$daysLeft hari, $hoursLeft jam, $minutesLeft mnt, $secondsLeft dtk"
        } else if (hoursLeft > 0) {
            "$hoursLeft jam, $minutesLeft mnt, $secondsLeft dtk"
        } else {
            "$minutesLeft mnt, $secondsLeft dtk"
        }
    } else {
        "Event Telah Berakhir!"
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(180.dp)
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = MaterialTheme.shapes.medium
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Background Image
            if (event.imageUrl != null) {
                AsyncImage(
                    model = event.imageUrl,
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
                
                // Gradient overlay for text readability
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.8f)),
                                startY = 100f
                            )
                        )
                )
            } else {
                // Fallback local image if no URL
                val fallbackRes = if (event.type.name == "BANNER") com.example.gachalendar.R.drawable.placeholder_banner else com.example.gachalendar.R.drawable.placeholder_event
                androidx.compose.foundation.Image(
                    painter = androidx.compose.ui.res.painterResource(id = fallbackRes),
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
                
                // Gradient overlay for text readability
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.8f)),
                                startY = 100f
                            )
                        )
                )
            }

            // Time left badge (Top Right)
            Surface(
                color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.9f),
                shape = MaterialTheme.shapes.small,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(8.dp)
            ) {
                Text(
                    text = timeLeftText,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }

            // Event Details (Bottom)
            Column(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text(
                    text = event.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (event.imageUrl != null) Color.White else MaterialTheme.colorScheme.onSecondaryContainer,
                    maxLines = 1
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Gim: ${event.gameId.uppercase()} | Tipe: ${if (event.type.name == "BANNER") "Banner Karakter" else "Event Dalam Gim"}",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (event.imageUrl != null) Color.LightGray else MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.8f)
                )
            }
        }
    }
}
